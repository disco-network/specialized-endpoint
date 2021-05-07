from typing import List

from .repositories import NodeRepository
from .domain.objects import Node, NodeData, Link, LinkType
from .domain.cache import Cache

from .dataspecs import Result, AggregateDataType, IntDataType, ListDataType, Nullable, StringDataType

#
# This file contains the specification and implementation of the API
# that is used for client-server communication.
#
# The API consists of `Commands`.
# Each `Command` consists of a data type specification
# (usually, as an AggregateDataType) and an `execute`
# function that takes an instance of the `Command` and
# the node repository (think: "database") it operates on.
#

GetNodesCommand = AggregateDataType({
    "ids": ListDataType(StringDataType),
    "depth": IntDataType,
}, lambda cmd: Result.ensure([
    (cmd["depth"] >= 0, "The depth must be nonnegative"),
    (cmd["depth"] <= 10, "The depth must be at most 10"),
]))

def executeGetNodesCommand(cmd, repository):
    cache = Cache.createEmpty()
    depthOfLevel = cmd["depth"]
    nodeCount = 0
    idsOnLevel = []

    def assignIdsForNextLevel(ids):
        nonlocal nodeCount, depthOfLevel, idsOnLevel
        if nodeCount + len(ids) >= 2000:
            depthOfLevel = 0
            idsOnLevel = ids[0:2000-nodeCount]
        else:
            idsOnLevel = ids
        nodeCount += len(idsOnLevel)
    assignIdsForNextLevel(cmd["ids"])

    while depthOfLevel >= 0:
        newIdsOnLevel = [id for id in idsOnLevel if not Cache.hasNode(cache, id)]
        newNodesOnLevel = repository.get(newIdsOnLevel)
        for (id, node) in newNodesOnLevel.items():
            Cache.storeNode(cache, node)

        depthOfLevel -= 1
        if depthOfLevel >= 0:
            idsWithUnknownChildrenOnLevel = [id for id in idsOnLevel if not Cache.hasChildrenOf(cache, id)]
            for (id, children) in repository.getChildren(idsWithUnknownChildrenOnLevel).items():
                Cache.storeChildren(cache, id, children)

            assignIdsForNextLevel([link["targetId"] for parentId in idsOnLevel for link in Cache.getChildrenOf(cache, parentId)])

    return cache


CreateNodeCommand = AggregateDataType({
    "nodeData": NodeData,
    "parentId": Nullable(StringDataType),
}, lambda cmd: Result.success(None))

def executeCreateNodeCommand(cmd, repository: NodeRepository) -> Node:
    node = repository.create(cmd["nodeData"])

    if cmd["parentId"].hasValue():
        link = Link.create({
            "sourceId": cmd["parentId"].extract(),
            "targetId": node["id"],
            "type": "general"
        })

        repository.link(link)

    return node

LinkCommand = AggregateDataType({
    "links": ListDataType(Link),
}, lambda data: Result.ensure([
    (len(data["links"]) <= 100, "The number of links given must not be higher than 100."),
]))

def executeLinkCommand(cmd, repository: NodeRepository):
    for link in cmd["links"]:
        repository.link(link)

UnlinkCommand = AggregateDataType({
    "links": ListDataType(Link),
}, lambda data: Result.ensure([
    (len(data["links"]) <= 100, "The number of links given must not be higher than 100."),
]))

def executeUnlinkCommand(cmd, repository: NodeRepository):
    for link in cmd["links"]:
        repository.unlink(link)

MoveCommand = AggregateDataType({
    "oldLinks": ListDataType(Link),
    "newLinks": ListDataType(Link),
}, lambda data: Result.ensure([
    (len(data["oldLinks"]) + len(data["newLinks"]) <= 200, "The total number of links given must not be higher than 200."),
]))

def executeMoveCommand(cmd, repository: NodeRepository):
    unlinkCmd = UnlinkCommand.create({
        "links": ListDataType(Link).serialize(cmd["oldLinks"]),
    })
    linkCmd = LinkCommand.create({
        "links": ListDataType(Link).serialize(cmd["newLinks"]),
    })

    executeUnlinkCommand(unlinkCmd, repository)
    executeLinkCommand(linkCmd, repository)

UpdateNodeDataCommand = AggregateDataType({
    "id": StringDataType,
    "data": NodeData,
}, lambda data: Result.success(None))

def executeUpdateNodeDataCommand(cmd, repository: NodeRepository):
    repository.update(cmd["id"], cmd["data"])


