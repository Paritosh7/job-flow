from celery import shared_task
from time import sleep
from jobs.models import Job, Item
from jobs.serializers import ItemSerializer
import logging
from rest_framework.renderers import JSONRenderer
from django.core.exceptions import ObjectDoesNotExist
from requests.exceptions import Timeout, ConnectionError

logger = logging.getLogger(__name__)

@shared_task(bind=True, queue='default', max_retries=3, retry_backoff=30, retry_backoff_max=300)
def async_job(self, job_id):
    try:
        logger.info(f"Doing an asynchronous job {job_id}")
        job = Job.objects.get(job_id=job_id)
        
        if self.request.retries == 0:
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
    
    # Remember retrying should be done for transient errors. 
    # Because of race condition maybe the job doesn't exist but it should be handled elsewhere
    # and it doesn't make sense for it to be retried. 
    except ObjectDoesNotExist as e:
        logger.error(f"Job {job_id} doesn't exist")
        return
    
    # Retrying should only be done for transient or temporary errors.
    except (ConnectionError, Timeout) as e:
        logger.warning(f"Retrying job {job_id} due to {e}")
        job.status = 'retrying'
        job.result = {"error":str(e)}
        job.save()
        raise self.retry(exc=e)
    
    except Exception as e:
        logger.error(f"Failure for {job_id} : {e}")
        job.status = 'failure'
        job.result = {"error": str(e)}
        job.save()
        return