from django.urls import path
from jobs import views

urlpatterns = [
    path('submit/', views.submit_job),
    path('item_list/', views.item_list),
    path('item_detail/<uuid:pk>', views.item_detail)
]
