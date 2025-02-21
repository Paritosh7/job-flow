from django.db import models
import uuid

# Create your models here.
class Job(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    task_name = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    
class JobResult(models.Model):
    job = models.OneToOneField(Job,on_delete=models.CASCADE)
    result = models.JSONField
    completed_at = models.DateTimeField(auto_now_add=True)
    