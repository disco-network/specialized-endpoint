import json
import traceback
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from .models import Node as DBNode, Link as DBLink
from .repositories import NodeRepository
from .api import executeGetNodesCommand, GetNodesCommand, executeCreateNodeCommand, CreateNodeCommand, UnlinkCommand, LinkCommand, MoveCommand, UpdateNodeDataCommand, executeUnlinkCommand
from .domain.objects import Node, Link
from .domain.cache import Cache

from .validation import Guard, ValidationException

nodeRepository = NodeRepository()

def createNode(request):
    try:
        command = CreateNodeCommand.create(getRawCommand(request))
        node = executeCreateNodeCommand(command, nodeRepository)
        return JsonResponse(Node.serialize(node))

    except ValidationException:
        return HttpResponse(status=400)

def deleteLinks(request):
    try:
        command = UnlinkCommand.create(getRawCommand(request))
        executeUnlinkCommand(command, nodeRepository)

        return HttpResponse(status=204)

    except ValidationException:
        return HttpResponse(status=400)

def addLinks(request):
    try:
        command = LinkCommand.create(getRawCommand(request))
        command.execute(nodeRepository)

        return HttpResponse(status=204)

    except ValidationException:
        return HttpResponse(status=400)

def moveLinks(request):
    try:
        command = MoveCommand.create(getRawCommand(request))
        command.execute()
        return HttpResponse(204)

    except ValidationException:
        return HttpResponse(status=400)

def updateNode(request):
    try:
        command = UpdateNodeDataCommand.create(getRawCommand(request))
        command.execute()
        return HttpResponse(status=204)
    except NodeNotFoundException:
        return HttpResponse(status=404)
    except ValidationException:
        return HttpResponse(status=400)

def getNodes(request):
    try:
        command = GetNodesCommand.create(getRawCommand(request))
        resultCache = executeGetNodesCommand(command, nodeRepository)
        return JsonResponse(Cache.serialize(resultCache))
    except ValidationException:
        print("ValidationException:")
        traceback.print_exc()
        return HttpResponse(status=400)

def getRawCommand(request):
    return json.loads(Guard.access(request.GET, "command"))

