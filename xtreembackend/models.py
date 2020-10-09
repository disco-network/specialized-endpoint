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

    parents = models.ManyToManyField("self", related_name="children", symmetrical=False, blank=True, through="Link")

    def addParent(self, parentId):
        if not Link.objects.filter(from_node_id=parentId, to_node_id=self.id).exists():
            link = Link(from_node_id=parentId, to_node_id=self.id)
            link.full_clean()
            link.save()
        else:
            link = Link.objects.get(from_node_id=parentId, to_node_id=self.id)
            link.deleted = False
            link.save()

    def __str__(self):
        return self.title

class Link(models.Model):
    TYPE_CHOICES = (
        ("general", "general"),
        ("pro_arg", "pro_arg"),
        ("con_arg", "con_arg"),
    )

    type = models.CharField(max_length=20, default="general", choices=TYPE_CHOICES)
    to_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="referredFrom")
    from_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="refersTo")

    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "xtreembackend_node_x_link"
        unique_together = ('type', 'to_node', 'from_node')

