import json
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from .models import Node as DBNode, Link as DBLink
from .repositories import NodeRepository
from .api import GetNodesCommand, CreateNodeCommand, UnlinkCommand, LinkCommand, MoveCommand, UpdateNodeDataCommand

from .domain.validation import Guard, ValidationException
from .domain.serialization import NodeSerializationService, CacheSerializationService

nodeRepository = NodeRepository()

def createNode(request):
    try:
        command = CreateNodeCommand.deserialize(getRawCommand(request))
        node = command.execute(nodeRepository)
        return JsonResponse(NodeSerializationService.serialize(node))

    except ValidationException:
        return HttpResponse(status=400)

def deleteLinks(request):
    try:
        command = UnlinkCommand.deserialize(getRawCommand(request))
        command.execute(nodeRepository)

        return HttpResponse(status=204)

    except ValidationException:
        return HttpResponse(status=400)

def addLinks(request):
    try:
        command = LinkCommand.deserialize(getRawCommand(request))
        command.execute(nodeRepository)

        return HttpResponse(status=204)

    except ValidationException:
        return HttpResponse(status=400)

def moveLinks(request):
    try:
        command = MoveCommand.deserialize(getRawCommand(request))
        command.execute()
        return HttpResponse(204)

    except ValidationException:
        return HttpResponse(status=400)

def updateNode(request):
    try:
        command = UpdateNodeDataCommand.deserialize(getRawCommand(request))
        command.execute()
        return HttpResponse(status=204)
    except NodeNotFoundException:
        return HttpResponse(status=404)
    except ValidationException:
        return HttpResponse(status=400)

def getNodes(request):
    try:
        command = GetNodesCommand.deserialize(getRawCommand(request))
        resultCache = command.execute()
        return JsonResponse(CacheSerializationService.serialize(resultCache))
    except ValidationException:
        return HttpResponse(status=400)

def getRawCommand(request):
    return json.loads(Guard.access(request.GET, "command"))

