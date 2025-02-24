from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/<int:event_id>/participate/', views.participate, name='event_participate'),
    path('create/', views.create_event, name='create_event'),
   
]
