from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from jobs.tasks import async_job
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from jobs.models import Item, Job
from jobs.serializers import ItemSerializer, JobSerializer
from django.db import transaction
from rest_framework.renderers import JSONRenderer
from django.core.cache import cache
import logging
from datetime import datetime, timedelta
from rest_framework.exceptions import ParseError
from rest_framework.views import APIView
from ..utils.cache_utils import get_cache_key

logger = logging.getLogger(__name__)


class ItemDetail(APIView):
    
    def get(self, request, pk):
        cache_key = get_cache_key(pk=pk)
        cached_item = cache.get(cache_key)
        
        if cached_item:
            logger.debug(f"Cache hit for item with id {pk}")
            return Response(cached_item, status=status.HTTP_200_OK)
        
        try:
            item = Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        logger.debug(f"Database hit for item with id {pk}")
        serializer = ItemSerializer(item)
        cache.set(cache_key, serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        try:
            item = Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            logger.error(f"Item with id {pk} doesn't exist")
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = ItemSerializer(item, data = request.data)
        if serializer.is_valid():
            serializer.save()
            
            cache_key = get_cache_key(pk)
            cache.set(cache_key, serializer.data)
            cache.expire_at(cache_key, datetime.now() + timedelta(hours=1))
            
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        
        else:  
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
    def delete(self, request, pk):
        
        try:
            item = Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            logger.error(f"Item with id {pk} doesn't exist")
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        item.delete()
        
        cache_key = get_cache_key(pk=pk)
        if cache_key:
            cache.delete(cache_key)
            
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class ItemList(APIView):
    
    def get(self, request):
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def post(self, request):
        serializer = ItemSerializer(data=request.data)
        
        if serializer.is_valid():
            item = serializer.save()
            
            cache_key = get_cache_key(item.id)
            cache.set(cache_key, serializer.data)
            cache.expire_at(cache_key, datetime.now() + timedelta(hours=1))
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        