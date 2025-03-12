from rest_framework.views import APIView
from jobs.models import Job
from rest_framework.response import Response
from rest_framework import status
from ..serializers import JobSerializer
from ..tasks import async_job
from django.db import transaction


class JobDetail(APIView):
    
    def get(self, request, pk):
        
        try:
            job = Job.objects.get(pk=pk)
        except Job.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = JobSerializer(job)
        
        return Response(serializer.data, status= status.HTTP_200_OK)
    
    
class SubmitJob(APIView):
    @transaction.atomic
    
    def post(self, request):
        
        serialiser = JobSerializer(data=request.data)
        if serialiser.is_valid():
            
            job_name = serialiser.data.get('job_name')
            
            job = Job.objects.create(job_name=job_name, status="pending")
            
            async_job.delay_on_commit(job.job_id)
            
            return Response(serialiser.data, status=status.HTTP_200_OK)
        
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)