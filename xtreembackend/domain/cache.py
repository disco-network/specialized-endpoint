from typing import List, Dict, Any

from xtreembackend.validation import ValidationException
from xtreembackend.dataspecs import AggregateDataType, MapDataType, IntDataType, ListDataType, Result

from xtreembackend.domain.objects import Node, Link

def haveAllLinksParentId(links, parentId):
    return all(map(lambda l: l["sourceId"] == parentId, links))

Cache = AggregateDataType({
    "nodesById": MapDataType(IntDataType, Node),
    "childrenByParentId": MapDataType(IntDataType, ListDataType(Link)),
}, lambda cache: Result.ensure([
    (all(map(lambda parentId: haveAllLinksParentId(cache["childrenByParentId"], parentId), cache["childrenByParentId"])), "childrenByParentId should map a parent ID only to links with the given parent ID"),
]))

def extendCache():
    def createEmpty():
        return {
            "nodesById": {},
            "childrenByParentId": {},
        }

    def copy(cache):
        return {
            "nodesById": dict(cache["nodesById"]),
            "childrenByParentId": dict(cache["childrenByParentId"]),
        }

    def storeNode(cache, node):
        cache["nodesById"][node["id"]] = node

    def hasNode(cache, nodeId):
        return nodeId in cache["nodesById"]

    def getNode(cache, nodeId):
        return cache["nodesById"][nodeId] if Cache.hasNode(cache, nodeId) else None

    def storeChildren(cache, nodeId: int, children):
        cache["childrenByParentId"][nodeId] = children

    def hasChildrenOf(cache, nodeId: int):
        return nodeId in cache["childrenByParentId"]

    def getChildrenOf(cache, nodeId):
        return cache["childrenByParentId"][nodeId] if Cache.hasChildrenOf(cache, nodeId) else None

    Cache.createEmpty = createEmpty
    Cache.copy = copy
    Cache.storeNode = storeNode
    Cache.hasNode = hasNode
    Cache.getNode = getNode
    Cache.storeChildren = storeChildren
    Cache.hasChildrenOf = hasChildrenOf
    Cache.getChildrenOf = getChildrenOf

extendCache()

