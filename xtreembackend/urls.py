from django.urls import path

from . import views

app_name="xtreembackend"
urlpatterns = [
    path("api/nodes/get", views.getNodes, name="getNodes"),
    path("api/nodes/create", views.createNode, name="createNode"),
    path("api/nodes/delete", views.deleteNode, name="deleteNode"),
    path("api/nodes/update", views.updateNode, name="updateNode"),
]

