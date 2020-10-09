from django.test import TestCase

from .repositories import NodeRepository
from .api import CreateNodeCommand, GetNodesCommand
from .domain.objects import Node, NodeData, NodeService, NodeType, Link, LinkType

class CommandTestCase(TestCase):
    def test(self):
        repo = NodeRepository()

        parentId = None
        for i in range(3):
            title = "Title " + str(i)
            content = "Content " + str(i)
            type = NodeType.GENERAL
            createCmd = CreateNodeCommand.make(
                nodeData=NodeService.makeData(title=title, content=content, type=type),
                parentId=parentId)
            node = createCmd.execute(repo)
            parentId = node.id

        getCmd = GetNodesCommand.make(
            ids=[1],
            depth=1)
        cache = getCmd.execute(repo)

        self.assertTrue(cache.hasNode(1), "Node 1 is in resulting cache")
        self.assertTrue(cache.hasNode(2), "Node 2 is in resulting cache")
        self.assertTrue(not cache.hasNode(3), "Node 3 is not in resulting cache")
        self.assertEqual(cache.getNode(1).data.title, "Title 0", "Node 1 has the correct title")
        self.assertListEqual([cache.getChildrenOf(1)[0].targetId], [2], "Node 2 is a child of node 1")
        self.assertFalse(cache.hasChildrenOf(2), "The children of node 2 are not in the cache")

"""
Ideas for more unit tests:
==========================

* Behavior when the GetNodesCommand execution exceeds the limit of 2000 queried nodes
  * Should it be allowed that nodes appear in the child list but are not part of the cache?
* Behavior when a node that was queried with GetNodesCommand does not exist
* Behavior when errors occur due to lack of transactionality
"""
