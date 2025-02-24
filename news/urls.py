from django.urls import path
from . import views


app_name = 'news'
urlpatterns = [

    # path('info/', views.radio_info_view, name='radio_info'),
    path('create_news', views.create_news, name='create_news'),
    path('news/', views.collect_news, name='news'),
]
