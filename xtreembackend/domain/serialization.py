from .objects import Node, NodeData, Link
from .cache import Cache

class NodeSerializationService:
    @staticmethod
    def serializeData(data: NodeData):
        return {
            "title": data.title,
            "content": data.content,
            "type": data.type.value,
        }

    @staticmethod
    def deserializeData(raw) -> NodeData:
        return NodeService.makeData(
            title=Guard.access(raw, "title"),
            content=Guard.access(raw, "content"),
            type=NodeType(Guard.access(raw, "type")))

    @staticmethod
    def serialize(node: Node):
        return {
            "id": node.id,
            "data": NodeSerializationService.serializeData(node.data),
        }

    @staticmethod
    def deserialize(raw) -> Node:
        return NodeService.make(
            id=Guard.access(raw, "id"),
            data=Guard.access(raw, "data"))

class LinkSerializationService:
    @staticmethod
    def serialize(link: Link):
        return {
            "sourceId": link.sourceId,
            "targetId": link.targetId,
            "type": link.type.value,
        }

    @staticmethod
    def deserialize(raw) -> Link:
        return LinkService.make(
            sourceId=Guard.access(raw, "sourceId"),
            targetId=Guard.access(raw, "targetId"),
            type=LinkType(Guard.access(raw, "type")))

class CacheSerializationService:
    @staticmethod
    def serialize(cache: Cache):
        return {
            "nodesById": mapDictValues(lambda node: NodeSerializationService.serialize(node), cache.nodesById),
            "childrenByParentId": mapDictValues(lambda children: map(lambda link: LinkSerializationService.serialize(link), children), cache.childrenByParentId),
        }

    @staticmethod
    def deserialize(raw) -> Cache:
        rawNodesById = Guard.access(raw, "nodesById")
        rawChildrenByParentId = Guard.access(raw, "childrenByParentId")

        if isDictOf(rawNodesById, lambda k: isinstance(k, int), lambda v: isinstance(v, dict)) and \
           isDictOf(rawChildrenByParentId,
                    lambda k: isinstance(k, int),
                    lambda v: isListOf(v, lambda link: isinstance(link, dict))):
            nodesById = mapDictValues(lambda rawNode: NodeSerializationService.deserialize(rawNode), Guard.access(raw, "nodesById"))
            childrenByParentId = mapDictValues(lambda rawChildren: map(lambda rawLink: LinkSerializationService.deserialize(rawLink), rawChildren), rawChildrenByParentId)

            return Cache.make(nodesById=nodesById, childrenByParentId=childrenByParentId)
        else:
            raise ValidationException()
