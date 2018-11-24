from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from xtreembackend.models import Node
from xtreembackend.forms import NodeCreationForm

def createNode(request):
#    parentNodeId = int(request.GET.get("parentnodeid", None))
#    title = request.GET.get("name")
#    content = request.GET.get("content")
#    type = request.GET.get("type")
#
#    node = Node()
#    node.title = title
#    node.content = content
#    node.node_type = type
#    node.author = request.user
#
#    node.full_clean()
#    node.save()
#
#    if parentNodeId != None:
#        node.parents.add(parentNodeId)
#    node.full_clean()
#    node.save()

    form = NodeCreationForm(request.GET)
    if (form.is_valid()):
        node = Node();
        node.title = form.cleaned_data["name"]
        node.content = form.cleaned_data["content"]
        node.node_type = form.cleaned_data["type"]
        node.author = User.objects.get(id=form.cleaned_data["authorid"])
        node.full_clean()
        node.save()

        if form.cleaned_data["parentnodeid"] != None:
            node.parents.add(form.cleaned_data["parentnodeid"])
            node.full_clean()
            node.save()

    else:
        return HttpResponse("Bad Request (invalid parameters)", 404)

    return JsonResponse({
        "id": node.id,
        "name": node.title,
        "content": node.content,
        "type": node.node_type,
    })

def deleteNode(request):
    nodeId = int(request.GET.get("id", None))
    node = Node.objects.get(id=nodeId)
    
    node.delete()
    return HttpResponse("No content", 204)

def updateNode(request):
    nodeId = int(request.GET.get("id", None))
    node = Node.objects.get(id=nodeId)

    title = request.GET.get("name", None)
    content = request.GET.get("content", None)
    type = request.GET.get("type", None)

    if title != None:
        node.title = title
    if content != None:
        node.content = content
    if type != None:
        node.node_type = type

    node.full_clean()
    node.save()
    return HttpResponse("No content", 204)

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
    neededFields = request.GET.getlist("neededFields[]", ["name", "type", "author", "content"])
    ids = [int(x) for x in request.GET.getlist("ids[]")]

    options = {
        "include_id": True,
        "include_name": "name" in neededFields,
        "include_author": "author" in neededFields,
        "include_type": "type" in neededFields,
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
        "name": node.title,
        "type": node.node_type,
        "content": node.content,
        "author": node.author.id if node.author else None,
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

