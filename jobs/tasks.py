from celery import shared_task
from time import sleep
from jobs.models import Job, Item
from jobs.serializers import ItemSerializer
import logging
from rest_framework.renderers import JSONRenderer

@shared_task(bind=True, queue='default')
def async_job(self, job_id):
    try:
        logging.info("Doing an asynchronous job")
        job = Job.objects.get(job_id=job_id)
        job.status = 'started'
        job.save()
        
        # Simulating Asynchronous processing
        sleep(20)
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        result_data = serializer.data
        
        job.status = 'success'
        job.result = result_data
        job.save()
        
        return result_data
        
    except Exception as e:
        job.status = 'failure'
        job.result = {"error":str(e)}
        job.save()
        raise e