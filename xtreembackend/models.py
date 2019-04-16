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
    content = models.TextField(max_length=65535, blank=True)
    node_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="general")
    
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    parents = models.ManyToManyField("self", related_name="children", symmetrical=False, blank=True, through="Link")

    def __str__(self):
        return self.title

class Link(models.Model):
    to_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="referredFrom")
    from_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="refersTo")

    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "xtreembackend_node_x_link"
        unique_together = ('to_node', 'from_node')

