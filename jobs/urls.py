from django.urls import path
from jobs.views import item_views, job_views

urlpatterns = [
    path('item-list/', item_views.ItemList.as_view(), name="item-list"),
    path('item-detail/<uuid:pk>', item_views.ItemDetail.as_view(), name="item-detail"),
    path('submit-job/', job_views.SubmitJob.as_view(), name="submit-job"),
    path('get-job-result/<uuid:pk>',job_views.JobDetail.as_view(), name="get-job-result")
]
