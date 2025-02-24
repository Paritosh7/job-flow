from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
# Create your views here.
from .tasks import add


@api_view(['POST'])
def submit_job(request):
    print(request)
    add.delay(2,4)
    return Response('Added', status=status.HTTP_201_CREATED)
