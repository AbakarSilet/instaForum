from django.urls import path
from . import views

app_name= 'resources'
urlpatterns = [
    path('', views.resource_list, name='resource_list'),
    path('search/', views.search_resources, name='search_resources'),
    path('add/image/', views.add_image, name='add_image'),
    path('add/link/', views.add_link, name='add_link'),
    path('add/document/', views.add_document, name='add_document'),
    path('add/video/', views.add_video, name='add_video'),
    path('detail/<int:pk>/', views.resource_detail, name='resource_detail'),
]
