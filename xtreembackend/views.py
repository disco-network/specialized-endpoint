from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from xtreembackend.models import Node, Link
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
        response = HttpResponse()
        response.status_code = 404
        return response

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
    response = HttpResponse()
    response.status_code = 204
    return response

def deleteLink(request):
    nodeId = int(request.GET.get("id", None))
#    node = Node.objects.get(id=nodeId)

    parentId = int(request.GET.get("parentid", None))
#    parent = Node.objects.get(id=parentId)

#    node.parents.remove(parent)

    link = Link.objects.get(from_node=parentId, to_node=nodeId)
    link.deleted = True
    link.full_clean()
    link.save()

    response = HttpResponse()
    response.status_code = 204
    return response

def addLink(request):
    nodeId = int(request.GET.get("id", None))
    node = Node.objects.get(id=nodeId)

    targetParentId = int(request.GET.get("targetparentid", None))
    targetParent = Node.objects.get(id=targetParentId)

    node.parents.add(targetParent)

    response = HttpResponse()
    response.status_code = 204
    return response

def moveLink(request):
    nodeId = int(request.GET.get("id", None))
    node = Node.objects.get(id=nodeId)

    oldParentId = int(request.GET.get("oldparentid", None))
    oldParent = Node.objects.get(id=oldParentId)
    newParentId = int(request.GET.get("newparentid", None))
    newParent = Node.objects.get(id=newParentId)

    node.parents.remove(oldParent)
    node.parents.add(newParent)

    response = HttpResponse()
    response.status_code = 204
    return response

def cloneNode(request):
    nodeId = int(request.GET.get("id", None))
    node = Node.objects.get(id=nodeId)

    targetParentId = int(request.GET.get("targetparentid", None))
    targetParent = Node.objects.get(id=targetParentId)

    newNode = Node()
    newNode.title = node.title
    newNode.content = node.content
    newNode.node_type = node.node_type
    newNode.author = node.author
    newNode.full_clean()
    newNode.save()

    newNode.parents.add(targetParent)

    response = HttpResponse()
    response.status_code = 204
    return response

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
    response = HttpResponse()
    response.status_code = 204
    return response

def getNodes(request):
    (ids, options) = parseOptions(request)

    nodes = []
    for id in ids:
        getNodesRec(id, nodes, options["parentlevels"], options["childlevels"], options["show_deleted"])

    result = []
    for node in nodes:
        result.append(serializeToJson(node, options))
    return JsonResponse({ "nodes": result })

def parseOptions(request):
    neededFields = request.GET.getlist("neededFields[]", ["name", "type", "author", "content"])
    showDeleted = request.GET.get("showDeleted", 0)
    ids = [int(x) for x in request.GET.getlist("ids[]")]

    options = {
        "include_id": True,
        "include_name": "name" in neededFields,
        "include_author": "author" in neededFields,
        "include_type": "type" in neededFields,
        "include_content": "content" in neededFields,
        "show_deleted": showDeleted == "1",
        # TODO: error handling
        "parentlevels": int(request.GET.get("parentlevels", default=0)),
        "childlevels": int(request.GET.get("childlevels", default=0)),
    }

    return (ids, options)

def getNodesRec(id, nodes, parentdepth, childdepth, showDeleted):
    node = Node.objects.get(id=id)
    nodes.append(node)

    if childdepth > 0:
        for link in node.refersTo.all():
            child = link.referree
            if (not link.deleted) or showDeleted:
                getNodesRec(child.id, nodes, 0, childdepth - 1, showDeleted)

    if parentdepth > 0:
        for link in node.referredFrom.all():
            parent = link.referrer
            if (not link.deleted) or showDeleted:
                getNodesRec(parent.id, nodes, parentdepth - 1, 0, showDeleted)

def serializeToJson(node, options):
    fields = {
        "id": node.id,
        "name": node.title,
        "type": node.node_type,
        "content": node.content,
        "author": node.author.id if node.author else None,
    }

    showDeleted = options["show_deleted"]
    json = {
        "parents": [link.from_node.id for link in (node.referredFrom.all() if showDeleted else node.referredFrom.filter(deleted=False).all())],
        "children": [link.to_node.id for link in (node.refersTo.all() if showDeleted else node.refersTo.filter(deleted=False).all())],
    }

    for key in fields:
        option = "include_" + key
        if (option in options) and options[option]:
            json[key] = fields[key]

    return json

