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
            node.addParent(form.cleaned_data["parentnodeid"])
#            link = Link(from_node_id=form.cleaned_data["parentnodeid"], to_node_id=node.id)
#            link.full_clean()
#            link.save()

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

def deleteLinks(request):
    ids = [int(x) for x in request.GET.getlist("ids[]", [])]
    pids = [int(x) for x in request.GET.getlist("pids[]", [])]
    for (id, pid) in zip(ids, pids):
        link = Link.objects.get(from_node=pid, to_node=id)
        link.deleted = True
        link.full_clean()
        link.save()

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

    node.addParent(targetParentId)

    response = HttpResponse()
    response.status_code = 204
    return response

def addLinks(request):
    ids = [int(x) for x in request.GET.getlist("ids[]", [])]
    pids = [int(x) for x in request.GET.getlist("pids[]", [])]

    for (id, pid) in zip(ids, pids):
        node = Node.objects.get(id=id)
        node.addParent(pid)

    response = HttpResponse()
    response.status_code = 204
    return response

def moveLink(request):
    nodeId = int(request.GET.get("id", None))
    node = Node.objects.get(id=nodeId)
    oldParentId = int(request.GET.get("oldparentid", None))
    newParentId = int(request.GET.get("newparentid", None))

    node.addParent(newParentId)

    oldLink = Link.objects.get(from_node_id=oldParentId, to_node_id=nodeId)
    oldLink.delete()

    response = HttpResponse()
    response.status_code = 204
    return response

def moveLinks(request):
    ids = [int(x) for x in request.GET.getlist("ids[]", [])]
    opids = [int(x) for x in request.GET.getlist("opids[]", [])]
    npids = [int(x) for x in request.GET.getlist("npids[]", [])]
    if len(ids) > 100 or len(ids) != len(opids) or len(ids) != len(npids):
        response = HttpResponse()
        response.status_code = 400
        return response
    
    for (id, opid, npid) in zip(ids, opids, npids):
        node = Node.objects.get(id=id);
        Link.objects.get(from_node_id=opid, to_node_id=id).delete()
        node.addParent(npid)
        
    response = HttpResponse()
    response.status_code = 204
    return response

def cloneNodes(request):
    ids = [int(x) for x in request.GET.getlist("ids[]", [])]
    pids = [int(x) for x in request.GET.getlist("pids[]", [])]

    for (id, pid) in zip(ids, pids):
        node = Node.objects.get(id=id)
        parent = Node.objects.get(id=pid)
        newNode = Node()
        newNode.title = node.title
        newNode.content = node.content
        newNode.node_type = node.node_type
        newNode.author = node.author
        newNode.full_clean()
        newNode.save()

        newNode.addParent(pid)

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

    newNode.addParent(targetParentId)

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

    nodes = {}
    getNodesRec2(ids, nodes, options["parentlevels"], options["childlevels"], options["show_deleted"], options)

    return JsonResponse({ "nodes": nodes })

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

def getNodesRec2(ids, nodes, parentdepth, childdepth, showDeleted, options):
    query_ids = [id for id in ids if not (id in nodes)]
    extend_ids = set([id for id in ids if id in nodes and nodes[id]["child_depth"] < childdepth])

    retrieved = Node.objects.prefetch_related("refersTo", "referredFrom").filter(id__in=query_ids).all()
    unknowns = set()
    for node in retrieved:
        serialized = serializeToJson(node, options)
        nodes[str(node.id)] = serialized

        serialized["children"] = [str(link.to_node.id) for link in node.refersTo.all() if not link.deleted]
        if options["show_deleted"]:
            serialized["del_children"] = [str(link.to_node.id) for link in node.refersTo.all() if link.deleted ];

        extend_ids.add(str(node.id))

    for id in extend_ids:
        node = nodes[id]
        node["child_depth"] = childdepth
        if childdepth > 0:
            node["children_included"] = True
            for childId in node["children"]:
                if not (childId in nodes) and not (childId in ids):
                    unknowns.add(childId)
    
            if options["show_deleted"]:
                for childId in serialized["del_children"]:
                    if not (childId in nodes) and not (childId in ids):
                        unknowns.add(childId)

    if len(unknowns) > 0:
        getNodesRec2(unknowns, nodes, 0, childdepth - 1, showDeleted, options)

def getNodesRec(id, nodes, parentdepth, childdepth, showDeleted, options):
    node = Node.objects.get(id=id)
    serialized = serializeToJson(node, options)
    nodes.append(serialized)

    if childdepth > 0:
        for child_id in serialized["children"]:
            getNodesRec(child_id, nodes, 0, childdepth - 1, showDeleted, options)

    if parentdepth > 0:
        for link in node.referredFrom.all():
            parent = link.from_node
            if not link.deleted:
                getNodesRec(parent.id, nodes, parentdepth - 1, 0, showDeleted, options)

def serializeToJson(node, options):
    fields = {
        "id": str(node.id),
        "name": node.title,
        "type": node.node_type,
        "content": node.content,
        "author": str(node.author.id) if node.author else None,
    }

    json = {}

    for key in fields:
        option = "include_" + key
        if (option in options) and options[option]:
            json[key] = fields[key]

    return json

