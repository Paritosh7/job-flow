import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobflow.settings')

app = Celery('jobflow')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.task_routes = {
    'jobs.tasks.add' : {'queue': 'default'}
}

app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')