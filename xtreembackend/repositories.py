from typing import List

from .models import Node as DBNode, Link as DBLink
from .domain.objects import Node, NodeType, NodeData, Link, LinkType
from .validation import ValidationException

class NodeRepository:
    def get(self, ids: List[int]):
        query = DBNode.objects.filter(id__in=ids)
        nodesById = {}
        for id in ids:
            nodesById[id] = None
        for dbNode in query.all():
            nodesById[dbNode.id] = self._toDomainNode(dbNode)
        return nodesById

    def getChildren(self, ids: List[int]):
        query = DBLink.objects.filter(from_node_id__in=ids)
        linksByParentId = {}
        for id in ids:
            linksByParentId[id] = []
        for dbLink in query.all():
            linksByParentId[dbLink.from_node_id].append(self._toDomainLink(dbLink))
        return linksByParentId

    def create(self, data):
        dbNode = DBNode(title=data["title"], content=data["content"], node_type=data["type"])
        dbNode.full_clean()
        dbNode.save()

        return self._toDomainNode(dbNode)

    def link(self, link: Link):
        query = self._linkToQuery(link)
        if not query.exists():
            dbLink = DBLink(from_node_id=link["sourceId"], to_node_id=link["targetId"], type=link["type"])
            dbLink.full_clean()
            dbLink.save()
        else:
            dbLink = query.get()
            dbLink.deleted = False
            dbLink.save()

    def unlink(self, link: Link):
        query = self._linkToQuery(link)
        if query.exists():
            dbLink = query.get()
            dbLink.deleted = True

    def update(self, id: int, data) -> Node:
        query = DBNode.objects.filter(id=id)
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

    def _linkToQuery(self, link: Link):
        return DBLink.objects.filter(from_node_id=link["sourceId"], to_node_id=link["targetId"], type=link["type"])

    def _toDomainNode(self, dbNode: DBNode) -> Node:
        return Node.create({
            "id": dbNode.id,
            "data": {
                "title": dbNode.title,
                "content": dbNode.content,
                "type": dbNode.node_type,
            },
        })

    def _toDomainLink(self, dbLink: DBLink) -> Link:
        return Link.create({
            "id": dbLink.id,
            "sourceId": dbLink.from_node_id,
            "targetId": dbLink.to_node_id,
            "type": dbLink.type,
        })

class NodeNotFoundException(Exception):
    pass
