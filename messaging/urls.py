# messaging/urls.py
from django.urls import path
from . import views


app_name = 'messaging'

urlpatterns = [
    path('', views.user_messages, name='user_messages'),
    path('thread/<str:username>/', views.thread_detail, name='thread_detail'),
    path('search_users/', views.search_users, name='search_users'),
    

]

    

