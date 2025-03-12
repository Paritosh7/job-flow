from django.urls import path
from jobs.views import item_views

urlpatterns = [
    path('submit-job/', item_views.submit_job),
    path('item-list/', item_views.ItemList.as_view(), name="item-list"),
    path('item-detail/<uuid:pk>', item_views.ItemDetail.as_view(), name="item-detail"),
    path('get-job-result/<uuid:pk>', item_views.get_job_result)
]
