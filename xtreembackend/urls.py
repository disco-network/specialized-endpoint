from django.urls import path

from . import views

app_name="xtreembackend"
urlpatterns = [
    path("api/nodes", views.getNodes, name="nodes"),
]

