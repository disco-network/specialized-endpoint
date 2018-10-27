from django import forms

from .models import Node

class NodeCreationForm(forms.Form):
    name = forms.CharField(max_length=255)
    type = forms.CharField(max_length=20)
    content = forms.CharField(max_length=65535, required=False)
    parentnodeid = forms.IntegerField(required=False)
