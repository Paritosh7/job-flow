from celery import shared_task
from time import sleep

@shared_task(queue='default')
def add(x,y):
    sleep(60)
    return x+y