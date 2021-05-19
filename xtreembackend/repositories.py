from typing import List

from .models import Node as DBNode, Link as DBLink
from .domain.objects import LinkID, Node, NodeType, NodeData, Link, LinkType
from .validation import ValidationException

# Abstracts the database.
# Note that Django ids are integers, while the dataspec requires strings.
# So this class translates between these two formats.
class NodeRepository:
    def get(self, ids):
        ids = [int(id) for id in ids]
        query = DBNode.objects.filter(id__in=ids)
        nodesById = {}
        for id in ids:
            nodesById[str(id)] = None
        for dbNode in query.all():
            nodesById[str(dbNode.id)] = self._toDomainNode(dbNode)
        return nodesById

    def getChildren(self, ids):
        ids = [int(id) for id in ids]
        query = DBLink.objects.filter(from_node_id__in=ids)
        linksByParentId = {}
        for id in ids:
            linksByParentId[str(id)] = []
        for dbLink in query.all():
            if not dbLink.deleted:
                linksByParentId[str(dbLink.from_node_id)].append(self._toDomainLink(dbLink))
        return linksByParentId

    def create(self, data):
        dbNode = DBNode(title=data["title"], content=data["content"], node_type=data["type"])
        dbNode.full_clean()
        dbNode.save()

        return self._toDomainNode(dbNode)

    def link(self, link: Link):
        query = self._linkOrLinkIdToQuery(link)
        if not query.exists():
            dbLink = DBLink(from_node_id=int(link["sourceId"]), to_node_id=int(link["targetId"]), type=link["type"])
            dbLink.full_clean()
            dbLink.save()
        else:
            dbLink = query.get()
            dbLink.deleted = False
            dbLink.type = link["type"]
            dbLink.save()

    def unlink(self, linkID: LinkID):
        query = self._linkOrLinkIdToQuery(linkID)
        if query.exists():
            dbLink = query.get()
            dbLink.deleted = True
            dbLink.save()

    def update(self, id, data) -> Node:
        # TODO: It would be better to catch errors
        # parsing `id` as an integer.
        # same for _linkToQuery(), link(), get() and getChildren().
        query = DBNode.objects.filter(id=int(id, 10))
        if query.exists():
            node = query.get()
            node.title = data["title"]
            node.content = data["content"]
            node.node_type = data["type"]
            node.full_clean()
            node.save()
            return self._toDomainNode(node)
        else:
            raise NodeNotFoundException()

    def _linkOrLinkIdToQuery(self, link: Link):
        return DBLink.objects.filter(from_node_id=int(link["sourceId"]), to_node_id=int(link["targetId"]))

    def _toDomainNode(self, dbNode: DBNode) -> Node:
        return Node.create({
            "id": str(dbNode.id),
            "data": {
                "title": dbNode.title,
                "content": dbNode.content,
                "type": dbNode.node_type,
            },
        })

    def _toDomainLink(self, dbLink: DBLink) -> Link:
        return Link.create({
            "id": str(dbLink.id),
            "sourceId": str(dbLink.from_node_id),
            "targetId": str(dbLink.to_node_id),
            "type": dbLink.type,
        })

class NodeNotFoundException(Exception):
    pass
