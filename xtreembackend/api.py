from typing import List

from .repositories import NodeRepository
from .domain.objects import LinkID, Node, NodeData, Link, LinkType
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
# Here is an article that might motivate this architecture
# a posteriori:
# https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/
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

 # Either creates a new link or updates the type
 # of an existing one.
LinkCommand = AggregateDataType({
    "links": ListDataType(Link),
}, lambda data: Result.ensure([
    (len(data["links"]) <= 100, "The number of links given must not be higher than 100."),
]))

def executeLinkCommand(cmd, repository: NodeRepository):
    for link in cmd["links"]:
        repository.link(link)

UnlinkCommand = AggregateDataType({
    "links": ListDataType(LinkID),
}, lambda data: Result.ensure([
    (len(data["links"]) <= 100, "The number of links given must not be higher than 100."),
]))

def executeUnlinkCommand(cmd, repository: NodeRepository):
    for linkID in cmd["links"]:
        repository.unlink(linkID)

MoveCommand = AggregateDataType({
    "oldLinks": ListDataType(LinkID),
    "newLinks": ListDataType(Link),
}, lambda data: Result.ensure([
    (len(data["oldLinks"]) + len(data["newLinks"]) <= 200, "The total number of links given must not be higher than 200."),
]))

def executeMoveCommand(cmd, repository: NodeRepository):
    unlinkCmd = UnlinkCommand.create({
        "links": ListDataType(LinkID).serialize(cmd["oldLinks"]),
    })
    linkCmd = LinkCommand.create({
        "links": ListDataType(Link).serialize(cmd["newLinks"]),
    })

    executeUnlinkCommand(unlinkCmd, repository)
    executeLinkCommand(linkCmd, repository)

UpdateNodeDataCommand = AggregateDataType({
    "id": StringDataType,
    "title": Nullable(StringDataType),
    "content": Nullable(StringDataType),
}, lambda data: Result.success(None))

def executeUpdateNodeDataCommand(cmd, repository: NodeRepository):
    # retrieve current node data
    nodeData = repository.get([cmd["id"]])[cmd["id"]]["data"]

    # change the fields that are to be changed
    if cmd["title"].hasValue():
        nodeData["title"] = cmd["title"].extract()
    if cmd["content"].hasValue():
        nodeData["content"] = cmd["content"].extract()

    # store the modified node data
    repository.update(cmd["id"], nodeData)


