from django.db import models

class Node(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(max_length=65535)
    
    parents = models.ManyToManyField("self", related_name="children", symmetrical=False)

    def __str__(self):
        return self.title

