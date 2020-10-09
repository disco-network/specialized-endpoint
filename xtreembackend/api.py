from typing import List

from .repositories import NodeRepository
from .domain.objects import Node, NodeData, Link, LinkType
from .domain.validation import Guard, ValidationException, isListOf
from .domain.serialization import NodeSerializationService, LinkSerializationService
from .domain.cache import Cache

class GetNodesCommand:
    ids: List[int]
    depth: int

    def isValid(self):
        return isListOf(self.ids, lambda id: isinstance(id, int)) and \
            isinstance(self.depth, int) and \
            self.depth <= 10

    def execute(self, repository: NodeRepository) -> Cache:
        cache = Cache.make()
        depthOfLevel = self.depth
        nodeCount = 0
        idsOnLevel = None

        def assignIdsForNextLevel(ids):
            nonlocal nodeCount, depthOfLevel, idsOnLevel
            if nodeCount + len(ids) >= 2000:
                depthOfLevel = 0
                idsOnLevel = ids[0:2000-nodeCount]
            else:
                idsOnLevel = ids
            nodeCount += len(idsOnLevel)
        assignIdsForNextLevel(self.ids)

        while depthOfLevel >= 0:
            newIdsOnLevel = [id for id in idsOnLevel if not cache.hasNode(id)]
            newNodesOnLevel = repository.get(newIdsOnLevel)
            for (id, node) in newNodesOnLevel.items():
                cache.storeNode(node)

            depthOfLevel -= 1
            if depthOfLevel >= 0:
                idsWithUnknownChildrenOnLevel = [id for id in idsOnLevel if not cache.hasChildrenOf(id)]
                for (id, children) in repository.getChildren(idsWithUnknownChildrenOnLevel).items():
                    cache.storeChildren(id, children)

                assignIdsForNextLevel([link.targetId for parentId in idsOnLevel for link in cache.getChildrenOf(parentId)])

        return cache

    # private
    def __init__(self, **attributes):
        self.__dict__.update(attributes)

    @staticmethod
    def make(**kwargs) -> "GetNodesCommand":
        cmd = GetNodesCommand(ids=Guard.access(kwargs, "ids"), depth=Guard.access(kwargs, "depth"))

        if cmd.isValid():
            return cmd
        else:
            raise ValidationException()

    @staticmethod
    def serialize(cmd):
        return {
            "ids": cmd.ids,
        }

    @staticmethod
    def deserialize(raw) -> "GetNodesCommand":
        return GetNodesCommand.make(**raw)

class CreateNodeCommand:
    nodeData: NodeData
    parentId: int # nullable

    def isValid(self):
        return isinstance(self.nodeData, NodeData) and \
            (self.parentId == None or isinstance(self.parentId, int))

    def execute(self, repository: NodeRepository) -> Node:
        node = repository.create(self.nodeData)

        if self.parentId != None:
            repository.link(Link(sourceId=self.parentId, targetId=node.id, type=LinkType.GENERAL))

        return node

    # private
    def __init__(self, **attributes):
        self.__dict__.update(attributes)

    @staticmethod
    def make(**kwargs) -> "CreateNodeCommand":
        cmd = CreateNodeCommand(
            nodeData=Guard.access(kwargs, "nodeData"),
            parentId=Guard.access(kwargs, "parentId"))

        if cmd.isValid():
            return cmd
        else:
            raise ValidationException()

    @staticmethod
    def serialize(cmd):
        return {
            "nodeData": cmd.nodeData,
            "parentId": cmd.parentId,
        }

    @staticmethod
    def deserialize(raw):
        return CreateNodeCommand.make(**raw)

class LinkCommand:
    links: List[Link]

    def __init__(self, **attributes):
        self.__dict__.update(attributes)

    def isValid(self):
        return isListOf(self.links, lambda item: isinstance(item, Link)) and \
            len(self.links) <= 100

    def execute(self, repository: NodeRepository):
        for link in self.links:
            repository.link(link)

    @staticmethod
    def make(**kwargs) -> "LinkCommand":
        cmd = LinkCommand(
            links=Guard.access(kwargs, "links"))

        if cmd.isValid():
            return cmd
        else:
            raise ValidationException()

    @staticmethod
    def serialize(cmd):
        return {
            "links": map(lambda link: LinkSerializationService.serialize(link), self.links)
        }

    @staticmethod
    def deserialize(raw) -> "LinkCommand":
        rawLinks = Guard.access(raw["links"])
        if isinstance(rawLinks, list):
            links = map(lambda raw: LinkSerializationService.deserialize(raw), rawLinks)
            return LinkCommand.make(links=links)

class UnlinkCommand:
    links: List[Link]

    def __init__(self, **attributes):
        self.__dict__.update(attributes)

    def isValid(self):
        return isListOf(self.links, lambda item: isinstance(item, Link)) and \
            len(self.links) <= 100

    def execute(self, repository: NodeRepository):
        for link in self.links:
            repository.unlink(link)

    @staticmethod
    def make(**kwargs) -> "UnlinkCommand":
        cmd = LinkCommand(
            links=Guard.access(kwargs, "links"))

        if cmd.isValid():
            return cmd
        else:
            raise ValidationException()

    @staticmethod
    def serialize(cmd):
        return {
            "links": map(lambda link: LinkSerializationService.serialize(link), cmd.links)
        }

    @staticmethod
    def deserialize(raw) -> "LinkCommand":
        rawLinks = Guard.access(raw, "links")
        if isinstance(rawLinks, list):
            links = map(lambda raw: LinkSerializationService.deserialize(raw), rawLinks)
            return LinkCommand.make(links=links)

class MoveCommand:
    oldLinks: List[Link]
    newLinks: List[Link]

    def __init__(**attributes):
        self.__dict__.update(attributes)

    def isValid(self):
        return isListOf(self.oldLinks, lambda item: isinstance(item, Link)) and \
            isListOf(self.newLinks, lambda item: isinstance(item, Link)) and \
            len(self.oldLinks) + len(self.newLinks) <= 200

    def execute(self, repository: NodeRepository):
        unlinkCmd = UnlinkCommand.make(links=self.oldLinks)
        linkCmd = LinkCommand.make(links=self.newLinks)

        unlinkCmd.execute()
        linkCmd.execute()

    @staticmethod
    def make(**kwargs) -> "MoveCommand":
        cmd = MoveCommand(
            oldLinks=Guard.access(kwargs, "oldLinks"),
            newLinks=Guard.access(kwargs, "newLinks"))

        if cmd.isValid:
            return cmd
        else:
            raise ValidationException()

    @staticmethod
    def serialize(cmd):
        return {
            "oldLinks": map(lambda link: LinkSerializationService.serialize(link), cmd.oldLinks),
            "newLinks": map(lambda link: LinkSerializationService.serialize(link), cmd.newLinks),
        }

    @staticmethod
    def deserialize(raw) -> "MoveCommand":
        rawOldLinks = Guard.access(raw, "oldLinks")
        rawNewLinks = Guard.access(raw, "newLinks")
        if isinstance(rawOldLinks, list) and isinstance(rawNewLinks, list):
            oldLinks = map(lambda raw: LinkSerializationService.deserialize(raw), rawOldLinks)
            newLinks = map(lambda raw: LinkSerializationService.deserialize(raw), rawNewLinks)
            return MoveCommand.make(oldLinks=oldLinks, newLinks=newLinks)
        else:
            raise ValidationException()

class UpdateNodeDataCommand:
    id: int
    data: NodeData

    def __init__(self, **attributes):
        self.__dict__.update(attributes)

    def isValid(self):
        return isinstance(self.id, int) and \
            isinstance(self.data, NodeData)

    def execute(self, repository: NodeRepository):
        repository.update(self.id, self.data)

    @staticmethod
    def make(**kwargs) -> "UpdateNodeDataCommand":
        cmd = UpdateNodeDataCommand(
            id=id, data=Guard.access(kwargs, "data"))

        if cmd.isValid():
            return cmd
        else:
            raise ValidationException()

    @staticmethod
    def serialize(cmd):
        return {
            "id": cmd.id,
            "data": cmd.data,
        }

    @staticmethod
    def deserialize(raw) -> "UpdateNodeDataCommand":
        return UpdateNodeDataCommand.make(
            id=Guard.access(raw, "id"),
            data=NodeSerializationService.deserialize(Guard.access(raw, "data")))
