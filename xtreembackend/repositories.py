from typing import List

from .models import Node as DBNode, Link as DBLink
from .domain.objects import Node, NodeType, NodeData, NodeService, Link, LinkType, LinkService

class NodeRepository:
    def get(self, ids: List[int]) -> List[Node]:
        query = DBNode.objects.filter(id__in=ids)
        nodesById = {}
        for id in ids:
            nodesById[id] = None
        for dbNode in query.all():
            nodesById[dbNode.id] = self._toDomainNode(dbNode)
        return nodesById

    def getChildren(self, ids: List[int]) -> List[List[Link]]:
        query = DBLink.objects.filter(from_node_id__in=ids)
        linksByParentId = {}
        for id in ids:
            linksByParentId[id] = []
        for dbLink in query.all():
            linksByParentId[dbLink.from_node_id].append(self._toDomainLink(dbLink))
        return linksByParentId

    def create(self, data: NodeData) -> Node:
        dbNode = DBNode(title=data.title, content=data.content, node_type=data.type.value)
        dbNode.full_clean()
        dbNode.save()

        node = NodeService.make(id=dbNode.id, data=data)
        return node

    def link(self, link: Link):
        query = self._linkToQuery(link)
        if not query.exists():
            dbLink = DBLink(from_node_id=link.sourceId, to_node_id=link.targetId, type=link.type.value)
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

    def update(self, id: int, data: NodeData) -> Node:
        query = DBNode.objects.filter(id=id)
        if query.exists():
            node = query.get()
            node.title = data.title
            node.content = data.content
            node.node_type = data.type.value
            node.full_clean()
            node.save()

            return NodeService.make(id=id, data=data)
        else:
            raise NodeNotFoundException()

    def _linkToQuery(self, link: Link):
        return DBLink.objects.filter(from_node_id=link.sourceId, to_node_id=link.targetId, type=link.type.value)

    def _toDomainNode(self, dbNode: DBNode) -> Node:
        data = NodeService.makeData(title=dbNode.title, content=dbNode.content, type=NodeType(dbNode.node_type))
        return NodeService.make(id=dbNode.id, data=data)

    def _toDomainLink(self, dbLink: DBLink) -> Link:
        return LinkService.make(id=dbLink.id, sourceId=dbLink.from_node_id, targetId=dbLink.to_node_id, type=LinkType(dbLink.type))

class NodeNotFoundException(Exception):
    pass
