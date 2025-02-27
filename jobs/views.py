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

@csrf_exempt
def item_detail(request,  pk):
    """
    Retrieve, update or delete item
    """
    try:
        item = Item.objects.get(pk = pk)
    except Item.DoesNotExist:
        return HttpResponse(status=404)
    
    if request.method == 'GET':
        serializer = ItemSerializer(item)
        return JsonResponse(serializer.data)
    
    if request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = ItemSerializer(item, data=data)
        
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)

        return JsonResponse(serializer.errors, status=400)

    if request.method == 'DELETE':
        item.delete()
        return HttpResponse(status=204)
    
@csrf_exempt
def item_list(request):
    
    if request.method == 'GET':
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        return JsonResponse(serializer.data, safe=False)
        
    
    
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = ItemSerializer(data = data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
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
            
            return JsonResponse({"job_id": job.job_id, "job_name":job_name, "status": "pending"}, status=status.HTTP_201_CREATED)
        
        return JsonResponse(serializer.errors, status = 400)
