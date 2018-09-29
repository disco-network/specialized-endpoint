from django.http import JsonResponse
from django.shortcuts import render

from xtreembackend.models import Node

def getNodes(request):
    ids = [1]
    options = {
        "include_id": True,
        "include_title": True,
        "include_content": True,
    }

    result = {}
    for id in ids:
        node = Node.objects.get(id=id) 
        result[id] = serializeToJson(node, options)
    return JsonResponse(result)

def serializeToJson(node, options):
    fields = {
        "id": node.id,
        "title": node.title,
        "content": node.content,
    }

    json = {}

    for key in fields:
        option = "include_" + key
        if (option in options) and options[option]:
            json[key] = fields[key]

    return json

