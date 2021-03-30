from django.test import TestCase

from .repositories import NodeRepository
from .api import CreateNodeCommand, GetNodesCommand, LinkCommand, executeCreateNodeCommand, executeGetNodesCommand, executeLinkCommand
from .domain.objects import Node, NodeData, NodeType, Link, LinkType
from .domain.cache import Cache
from .dataspecs import MapDataType, ListDataType, IntDataType, StringDataType
from .validation import ValidationException

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

class LinkCommandTestCase(TestCase):
    def test_empty_list(self):
        repo = NodeRepository()

        node1 = repo.create(NodeData.create({
            "title": "One",
            "content": "Lorem",
            "type": "general",
        }))

        cmd = LinkCommand.create({
            "links": [],
        })

        executeLinkCommand(cmd, repo)

        linksToChildren = repo.getChildren([1])[1]

        self.assertEqual(len(linksToChildren), 0)

    def test_single_link(self):
        repo = NodeRepository()

        node1 = repo.create(NodeData.create({
            "title": "One",
            "content": "Lorem",
            "type": "general",
        }))

        node2 = repo.create(NodeData.create({
            "title": "Two",
            "content": "ipsum",
            "type": "general",
        }))

        cmd = LinkCommand.create({
            "links": [
                {
                    "sourceId": node1["id"],
                    "targetId": node2["id"],
                    "type": "general",
                },
            ],
        })

        executeLinkCommand(cmd, repo)

        allChildren = repo.getChildren([1, 2])
        linksToChildrenOfNode1 = allChildren[1]
        linksToChildrenOfNode2 = allChildren[2]

        self.assertEqual(len(linksToChildrenOfNode1), 1)
        self.assertEqual(len(linksToChildrenOfNode2), 0)
        self.assertEqual(linksToChildrenOfNode1[0]["sourceId"], node1["id"])
        self.assertEqual(linksToChildrenOfNode1[0]["targetId"], node2["id"])

    def test_create_link_that_already_exists_with_same_type(self):
        repo = NodeRepository()

        node1 = repo.create(NodeData.create({
            "title": "One",
            "content": "Lorem",
            "type": "general",
        }))

        node2 = repo.create(NodeData.create({
            "title": "Two",
            "content": "ipsum",
            "type": "general",
        }))

        repo.link(Link.create({
            "sourceId": node1["id"],
            "targetId": node2["id"],
            "type": "general",
        }))

        cmd = LinkCommand.create({
            "links": [
                {
                    "sourceId": node1["id"],
                    "targetId": node2["id"],
                    "type": "general",
                },
            ],
        })

        executeLinkCommand(cmd, repo)

        allChildren = repo.getChildren([1, 2])
        linksToChildrenOfNode1 = allChildren[1]
        linksToChildrenOfNode2 = allChildren[2]

        self.assertEqual(len(linksToChildrenOfNode1), 1)
        self.assertEqual(len(linksToChildrenOfNode2), 0)
        self.assertEqual(linksToChildrenOfNode1[0]["sourceId"], node1["id"])
        self.assertEqual(linksToChildrenOfNode1[0]["targetId"], node2["id"])
        self.assertEqual(linksToChildrenOfNode1[0]["type"], "general")
        
    def test_create_link_that_already_exists_with_different_type(self):
        repo = NodeRepository()

        node1 = repo.create(NodeData.create({
            "title": "One",
            "content": "Lorem",
            "type": "general",
        }))

        node2 = repo.create(NodeData.create({
            "title": "Two",
            "content": "ipsum",
            "type": "general",
        }))

        repo.link(Link.create({
            "sourceId": node1["id"],
            "targetId": node2["id"],
            "type": "general",
        }))

        cmd = LinkCommand.create({
            "links": [
                {
                    "sourceId": node1["id"],
                    "targetId": node2["id"],
                    "type": "pro_arg",
                },
            ],
        })

        executeLinkCommand(cmd, repo)

        allChildren = repo.getChildren([1, 2])
        linksToChildrenOfNode1 = allChildren[1]
        linksToChildrenOfNode2 = allChildren[2]

        self.assertEqual(len(linksToChildrenOfNode1), 2)
        self.assertEqual(len(linksToChildrenOfNode2), 0)
        self.assertEqual(linksToChildrenOfNode1[0]["sourceId"], node1["id"])
        self.assertEqual(linksToChildrenOfNode1[0]["targetId"], node2["id"])
        self.assertEqual(linksToChildrenOfNode1[0]["type"], "general")
        self.assertEqual(linksToChildrenOfNode1[1]["sourceId"], node1["id"])
        self.assertEqual(linksToChildrenOfNode1[1]["targetId"], node2["id"])
        self.assertEqual(linksToChildrenOfNode1[1]["type"], "pro_arg")

    def test_create_too_many_links(self):
        with self.assertRaisesMessage(ValidationException): # Problem: Must provide expected message!
            cmd = LinkCommand.create({
                "links": [
                    {
                        "sourceId": node1["id"],
                        "targetId": node2["id"],
                        "type": "general",
                    } for x in range(101)
                ],
            })        

class CreateNodeTestCase(TestCase):
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
