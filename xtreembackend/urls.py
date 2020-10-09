from django.urls import path

from . import views

app_name="xtreembackend"
urlpatterns = [
    path("api/nodes/get", views.getNodes, name="getNodes"),
    path("api/nodes/create", views.createNode, name="createNode"),
    path("api/nodes/update", views.updateNode, name="updateNode"),

    path("api/nodes/deleteLinks", views.deleteLinks, name="deleteLinks"),
    path("api/nodes/moveLinks", views.moveLinks, name="moveLinks"),
    path("api/nodes/addLinks", views.addLinks, name="addLinks"),
]

