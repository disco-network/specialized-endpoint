from django.test import TestCase

from .repositories import NodeRepository
from .api import CreateNodeCommand, GetNodesCommand, executeCreateNodeCommand, executeGetNodesCommand
from .domain.objects import Node, NodeData, NodeType, Link, LinkType
from .domain.cache import Cache
from .dataspecs import MapDataType, ListDataType, IntDataType, StringDataType
from .validation import extractOrThrow

class DataSpecTestCase(TestCase):
    def test_map(self):
        ismap = MapDataType(IntDataType, StringDataType)
        instance = ismap.create({1: "one", 2: "two"})
        serialized = ismap.serialize(instance)

        self.assertEqual(serialized[1], "one")

    def test_list(self):
        intlist = ListDataType(IntDataType)
        instance = intlist.create([1])
        serialized = intlist.serialize(instance)

        self.assertEqual(len(serialized), 1)
        self.assertEqual(serialized[0], 1)

class CommandTestCase(TestCase):
    def test(self):
        repo = NodeRepository()

        parentId = None
        for i in range(3):
            title = "Title " + str(i)
            content = "Content " + str(i)
            createCmd = CreateNodeCommand.create({
                "nodeData": {
                    "title": title,
                    "content": content,
                    "type": "general",
                },
                "parentId": parentId,
            })
            node = executeCreateNodeCommand(createCmd, repo)
            parentId = node["id"]

        getCmd = GetNodesCommand.create({
            "ids": [1],
            "depth": 1,
        })

        cache = executeGetNodesCommand(getCmd, repo)

        self.assertTrue(Cache.hasNode(cache, 1), "Node 1 is in resulting cache")
        self.assertTrue(Cache.hasNode(cache, 2), "Node 2 is in resulting cache")
        self.assertTrue(not Cache.hasNode(cache, 3), "Node 3 is not in resulting cache")
        self.assertEqual(Cache.getNode(cache, 1)["data"]["title"], "Title 0", "Node 1 has the correct title")
        self.assertListEqual([Cache.getChildrenOf(cache, 1)[0]["targetId"]], [2], "Node 2 is a child of node 1")
        self.assertFalse(Cache.hasChildrenOf(cache, 2), "The children of node 2 are not in the cache")

"""
Ideas for more unit tests:
==========================

* Behavior when the GetNodesCommand execution exceeds the limit of 2000 queried nodes
  * Should it be allowed that nodes appear in the child list but are not part of the cache?
* Behavior when a node that was queried with GetNodesCommand does not exist
* Behavior when errors occur due to lack of transactionality
"""
