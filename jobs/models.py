from django.db import models
import uuid

# Create your models here.

class Item(models.Model):
    id = models.UUIDField(default=uuid.uuid4,primary_key=True, editable=False)
    item_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateField(auto_now=True)


class Job(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    job_name = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default="pending")
    result = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    