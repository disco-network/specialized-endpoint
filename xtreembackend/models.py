from django.contrib.auth.models import User
from django.db import models

class Node(models.Model):
    TYPE_CHOICES = (
        ("general", "general"),
        ("topic", "topic"),
        ("fact", "fact"),
        ("pro_arg", "pro_arg"),
        ("con_arg", "con_arg"),
        ("question", "question"),
        ("problem", "problem"),
        ("idea", "idea"),
        ("aim", "aim"),
        ("region", "region")
    )

    title = models.CharField(max_length=255)
    content = models.TextField(max_length=65535)
    node_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="general")
    
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    parents = models.ManyToManyField("self", related_name="children", symmetrical=False, blank=True)

    def __str__(self):
        return self.title

