from rest_framework import serializers
from jobs.models import Item, Job

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'item_name', 'created_at', 'modified_at']
        read_only_fields = ['id', 'created_at', 'modified_at']
    
class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['job_id', 'job_name','status', 'result', 'created_at', 'modified_at']
        read_only_fields = ['job_id', 'status', 'result', 'created_at', 'modified_at']
        