from xtreembackend.dataspecs import Result, EnumDataType, ListDataType, IntDataType, StringDataType, AggregateDataType

NodeType = EnumDataType([
    "general",
    "topic",
    "fact",
    "pro_arg",
    "con_arg",
    "question",
    "problem",
    "idea",
    "aim",
    "region",
])

NodeData = AggregateDataType({
    "title": StringDataType,
    "content": StringDataType,
    "type": NodeType,
}, lambda data: Result.ensure([
    (len(data["title"]) <= 140, "The title must have less than or equal to 140 characters.")
]))

Node = AggregateDataType({
    "id": StringDataType,
    "data": NodeData,
}, lambda node: Result.success(None))

LinkType = EnumDataType([
    "general",
    "topic",
    "fact",
    "pro_arg",
    "con_arg",
    "question",
    "problem",
    "idea",
    "aim",
    "region",
])

LinkID = AggregateDataType({
    "sourceId": StringDataType,
    "targetId": StringDataType,
}, lambda link: Result.success(None))

# Link extends LinkID; the LinkID of a Link is unique.
Link = AggregateDataType({
    "sourceId": StringDataType, # ID of the parent
    "targetId": StringDataType, # ID of the child
    "type": LinkType,
}, lambda link: Result.success(None))

