from enum import Enum
from .validation import Guard, ValidationException

class NodeType(Enum):
    GENERAL = "general"
    TOPIC = "topic"
    FACT = "fact"
    PRO_ARG = "pro_arg"
    CON_ARG = "con_arg"
    QUESTION = "question"
    PROBLEM = "problem"
    IDEA = "idea"
    AIM = "aim"
    REGION = "region"

class LinkType(Enum):
    GENERAL = "general"
    PRO_ARG = "pro_arg"
    CON_ARG = "con_arg"


class NodeData:

    title: str
    content: str
    type: NodeType

    def __init__(self, **attributes):
        self.__dict__.update(attributes)

class Node:

    id: int
    data: NodeData

    def __init__(self, **attributes):
        self.__dict__.update(attributes)

class Link:

    # source is parent, target is child
    sourceId: int
    targetId: int
    type: LinkType

    def __init__(self, **attributes):
        self.__dict__.update(attributes)

class NodeService:

    @staticmethod
    def make(**kwargs):
        id = Guard.access(kwargs, "id")
        data = Guard.access(kwargs, "data")

        node = Node(id=id, data=data)
        if NodeService.isValid(node):
            return node
        else:
            raise ValidationException()

    @staticmethod
    def makeData(**kwargs):
        title = Guard.access(kwargs, "title")
        content = Guard.access(kwargs, "content")
        type = Guard.access(kwargs, "type")

        data = NodeData(title=title, content=content, type=type)
        if NodeService.areDataValid(data):
            return data
        else:
            raise ValidationException()

    @staticmethod
    def isValid(node: Node):
        return isinstance(node.id, int) and \
            isinstance(node.data, NodeData)

    @staticmethod
    def areDataValid(data: NodeData):
        return isinstance(data.title, str) and \
            isinstance(data.content, str) and \
            isinstance(data.type, NodeType) and \
            len(data.title) < 140 and \
            len(data.content) < 5000

class LinkService:

    @staticmethod
    def make(**kwargs):
        sourceId = Guard.access(kwargs, "sourceId")
        targetId = Guard.access(kwargs, "targetId")
        type = Guard.access(kwargs, "type")

        link = Link(sourceId=sourceId, targetId=targetId, type=type)
        if LinkService.isValid(link):
            return link
        else:
            raise ValidationException()

    @staticmethod
    def isValid(link):
        return isinstance(link.sourceId, int) and \
            isinstance(link.targetId, int) and \
            isinstance(link.type, LinkType)
