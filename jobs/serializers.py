from rest_framework import serializers
from jobs.models import Item

class ItemSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    item_name = serializers.CharField(max_length = 50)

    def create(self, validated_data):
        
        """Create a new item given the item_name

        Returns a new item instance given the validated_data
        """
        return Item.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        
        instance.item_name = validated_data.get('item_name', instance.item_name)
        instance.save()
        return instance
    
class JobSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    job_name = serializers.CharField(max_length = 20)
    status = serializers.CharField(max_length= 20)
    result = serializers.JSONField(required=False)
        