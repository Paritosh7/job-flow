from django.urls import path
from jobs import views

urlpatterns = [
    path('submit-job/', views.submit_job),
    path('item-list/', views.item_list),
    path('item-detail/<uuid:pk>', views.item_detail),
    path('get-job-result/<uuid:pk>', views.get_job_result)
]
