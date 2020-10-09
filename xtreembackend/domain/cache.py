from typing import List, Dict
from .objects import Node, Link
from .validation import ValidationException, isDictOf, isListOf

class Cache:
    nodesById: Dict[int, Node]
    childrenByParentId: Dict[int, List[Link]]

    @staticmethod
    def make(**kwargs):
        nodesById = kwargs["nodesById"] if "nodesById" in kwargs else {}
        childrenByParentId = kwargs["childrenByParentId"] if "childrenByParentId" in kwargs else {}
        cache = Cache(
            nodesById=nodesById,
            childrenByParentId=childrenByParentId)

        if cache.isValid():
            return cache
        else:
            raise ValidationException

    def isValid(self):
        def fst(kv):
            (k, v) = kv
            return k
        def snd(kv):
            (k, v) = kv
            return v
        def haveAllLinksParentId(links, parentId):
            return all(map(lambda l: l.sourceId == parentId, links))

        return isDictOf(self.nodesById,
                        lambda k: isinstance(k, int),
                        lambda v: isinstance(v, Node)) and \
            isDictOf(self.childrenByParentId,
                     lambda k: isinstance(k, int),
                     lambda v: isListOf(
                         lambda i: isinstance(i, Link))) and \
            all(map(lambda kv: haveAllLinksParentId(snd(kv), fst(kv)), self.childrenByParentId))

    def copy(self):
        return Cache(
            nodesById=dict(self.nodesById),
            childrenByParentId=dict(self.childrenByParentId))

    def storeNode(self, node: Node):
        self.nodesById[node.id] = node

    def hasNode(self, nodeId):
        return nodeId in self.nodesById

    def getNode(self, nodeId):
        return self.nodesById[nodeId] if self.hasNode(nodeId) else None

    def storeChildren(self, nodeId: int, children: List[Link]):
        self.childrenByParentId[nodeId] = children

    def hasChildrenOf(self, nodeId):
        return nodeId in self.childrenByParentId

    def getChildrenOf(self, nodeId):
        return self.childrenByParentId[nodeId] if self.hasChildrenOf(nodeId) else None

    # private
    def __init__(self, **attributes):
        self.__dict__.update(attributes)

def mapDictValues(fn, dictionary):
    def applyFnToSecondEntry(kv):
        (k, v) = kv
        return (k, fn(v))

    return dict(map(applyFnToSecondEntry, dictionary.items()))
