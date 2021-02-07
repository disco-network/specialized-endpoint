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
    "id": IntDataType,
    "data": NodeData,
}, lambda node: Result.success(None))

LinkType = EnumDataType([
    "general",
    "pro_arg",
    "con_arg",
])

Link = AggregateDataType({
    "sourceId": IntDataType,
    "targetId": IntDataType,
    "type": LinkType,
}, lambda link: Result.success(None))

