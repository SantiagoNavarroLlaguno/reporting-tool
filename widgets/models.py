from django.db import models
from django.contrib.auth.models import User

class Widget(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
