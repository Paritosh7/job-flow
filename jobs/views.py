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

logger = logging.getLogger(__name__)

def get_cache_key(pk):
    return f'item_{pk}'

@csrf_exempt
def item_detail(request,  pk):
    """
    Retrieve, update or delete item
    """
    
    cache_key = get_cache_key(pk=pk)
    cached_item = cache.get(cache_key)
    
    if cached_item and request.method == 'GET':
        logger.debug(f"cache hit for item with id {cached_item} and {cache_key}")
        return JsonResponse(cached_item)
    
    try:
        item = Item.objects.get(pk = pk)
    except Item.DoesNotExist:
        return HttpResponse(status=404)
    
    if request.method == 'GET':
        logger.debug(f"database hit for GET with id {cache_key}")
        serializer = ItemSerializer(item)
        return JsonResponse(serializer.data)
    
    if request.method == 'PUT':
        logger.debug(f"PUT request for id {pk}")
        data = JSONParser().parse(request)
        serializer = ItemSerializer(item, data=data)
        
        if serializer.is_valid():
            serializer.save()
                  
            cache.set(cache_key, serializer.validated_data)
            cache.expire_at(cache_key, datetime.now() + timedelta(hours=1))
            logger.debug(f"Cache set for id {cache_key}")
            
            return JsonResponse(serializer.data)

        return JsonResponse(serializer.errors, status=400)

    if request.method == 'DELETE':
        logger.debug(f"delete request for id {pk}")
        deletion_detail = item.delete()
        
        if cache.has_key(cache_key):
            cache.delete(cache_key)
            logger.debug(f"cache deleted for id {cache_key}")
        # safe false, as not returning key value pair and JsonResponse expects that.
        return JsonResponse(deletion_detail, status=204, safe= False)
    
@csrf_exempt
def item_list(request):
    
    if request.method == 'GET':
        logger.debug(f"GET request to list all items")
        
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        return JsonResponse(serializer.data, safe=False)
        
    
    
    if request.method == 'POST':
        # if request.body is empty JSONParser().parse(request) raises exception
        
        try:
            data = JSONParser().parse(request)
            serializer = ItemSerializer(data = data)
            
            if serializer.is_valid():
                logger.debug(f"POST request with data : {serializer.validated_data}")
                item = serializer.save()
                cache_key = get_cache_key(item.id)
                
                cache.set(cache_key, serializer.validated_data)
                cache.expire_at(cache_key, datetime.now() + timedelta(hours=1))

                return JsonResponse(serializer.validated_data, status=201)
        
        except ParseError as e:
            return JsonResponse({"error": "Empty JSON body"}, status=400)
            
        
        return JsonResponse(serializer.errors, status=400)
    

@csrf_exempt
def get_job_result(request, pk):
    
    try:
        job_item = Job.objects.get(pk=pk)
    except Job.DoesNotExist:
        return HttpResponse(status=404)
    
    if request.method == 'GET':
        serializer = JobSerializer(job_item)
        return JsonResponse(serializer.data)


@csrf_exempt
@transaction.atomic
def submit_job(request):
    
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = JobSerializer(data = data)
        if serializer.is_valid():
            job_name = serializer.validated_data['job_name']
            
            job = Job.objects.create(job_name=job_name, status="pending")
            
            async_job.delay_on_commit(job.job_id)
            
            return JsonResponse({"job_id": job.job_id, "job_name":job_name, "status": job.status}, status=status.HTTP_201_CREATED)
        
        return JsonResponse(serializer.errors, status = 400)
