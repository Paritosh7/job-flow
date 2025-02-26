from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .tasks import add
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from jobs.models import Item
from jobs.serializers import ItemSerializer

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


@api_view(['POST'])
def submit_job(request):
    print(request)
    add.delay(2,4)
    return Response('Added', status=status.HTTP_201_CREATED)
