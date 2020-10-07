from django.urls import path

from . import views

app_name="xtreembackend"
urlpatterns = [
    path("api/nodes/get", views.getNodes, name="getNodes"),
    path("api/nodes/create", views.createNode, name="createNode"),
    path("api/nodes/delete", views.deleteNode, name="deleteNode"),
    path("api/nodes/deleteLink", views.deleteLink, name="deleteLink"),
    path("api/nodes/deleteLinks", views.deleteLinks, name="deleteLinks"),
    path("api/nodes/update", views.updateNode, name="updateNode"),

    path("api/nodes/moveLink", views.moveLink, name="moveLink"),
    path("api/nodes/moveLinks", views.moveLinks, name="moveLinks"),
    path("api/nodes/cloneNode", views.cloneNode, name="cloneNode"),
    path("api/nodes/cloneNodes", views.cloneNodes, name="cloneNodes"),
    path("api/nodes/addLink", views.addLink, name="addLink"),
    path("api/nodes/addLinks", views.addLinks, name="addLinks"),
]

