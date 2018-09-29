from django.http import JsonResponse
from django.shortcuts import render

from xtreembackend.models import Node

def getNodes(request):
    (ids, options) = parseOptions(request)

    nodes = {}
    for id in ids:
        getNodesRec(id, nodes, options["parentlevels"], options["childlevels"])

    result = {}
    for id in nodes:
        node = nodes[id]["node"]
        result[id] = serializeToJson(node, options)
    return JsonResponse(result)

def parseOptions(request):
    neededFields = request.GET.getlist("neededFields[]", ["title", "content"])
    ids = [int(x) for x in request.GET.getlist("ids[]")]

    options = {
        "include_id": True,
        "include_title": "title" in neededFields,
        "include_content": "content" in neededFields,
        # TODO: error handling
        "parentlevels": int(request.GET.get("parentlevels", default=0)),
        "childlevels": int(request.GET.get("childlevels", default=0)),
    }

    return (ids, options)

def getNodesRec(id, nodes, parentdepth, childdepth):
    if not id in nodes:
        nodes[id] = {
            "node": Node.objects.get(id=id),
            "childdepth": 0,
            "parentdepth": 0
        }

    if nodes[id]["childdepth"] < childdepth:
        nodes[id]["childdepth"] = childdepth
        for child in nodes[id]["node"].children.all():
            getNodesRec(child.id, nodes, 0, childdepth - 1)

    if nodes[id]["parentdepth"] < parentdepth:
        nodes[id]["parentdepth"] = parentdepth
        for parent in nodes[id]["node"].parents.all():
            getNodesRec(parent.id, nodes, parentdepth - 1, 0)

def serializeToJson(node, options):
    fields = {
        "id": node.id,
        "title": node.title,
        "content": node.content,
    }

    json = {
        "parents": [parent.id for parent in node.parents.all()],
        "children": [child.id for child in node.children.all()],
    }

    for key in fields:
        option = "include_" + key
        if (option in options) and options[option]:
            json[key] = fields[key]

    return json

