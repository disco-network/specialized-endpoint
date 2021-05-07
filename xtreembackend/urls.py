from django.urls import path

from . import views

app_name="xtreembackend"
urlpatterns = [
    path("api/nodes/get", views.getNodes, name="getNodes"),
    path("api/nodes/create", views.createNode, name="createNode"),
    path("api/nodes/update", views.updateNode, name="updateNode"),

    path("api/links/delete", views.deleteLinks, name="deleteLinks"),
    path("api/links/move", views.moveLinks, name="moveLinks"),
    path("api/links/add", views.addLinks, name="addLinks"),
]

