from django.urls import path
from .views import create_thread, add_post_view, first_thread_congrats, forum_home_view, mark_as_read, notifications, profile_view, report_view, search_view, subforum_view, create_thread_view, tagged, thread_view,delete_thread_view
from .views import like_thread, dislike_thread
from forum import views

app_name = 'forum'

urlpatterns = [
    path('', forum_home_view, name='home'),
    path('subforum/<slug>/', subforum_view, name='subforum'),
    path('subforum/<slug>/create_thread/', create_thread_view, name='create_thread'),
    path('create/', create_thread, name='create'), 
    path('thread/<slug:slug>/', thread_view, name='thread'),
    path('add_post/<int:thread_id>/', add_post_view, name='add_post'),
    path('delete/<slug:slug>/',delete_thread_view,name='delete_thread'),
    
    path('thread/update/<slug:slug>/', views.update_thread, name='update_thread'),
    path('post/update/<int:post_id>/', views.update_post, name='update_post'),
    
    path('search/', search_view, name='search'),
    path('profile/<str:username>/', profile_view, name='profile'),
    path('tag/<slug:slug>/', tagged, name='tagged'),
    path('report/<str:report_type>/<int:item_id>/', report_view, name='report'),
    path('first-thread-congrats/<slug:slug>/', first_thread_congrats, name='first_thread_congrats'),

    path('thread/<int:thread_id>/like/', like_thread, name='like_thread'),
    path('thread/<int:thread_id>/dislike/', dislike_thread, name='dislike_thread'),

    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('suspend_user/<int:user_id>/', views.suspend_user, name='suspend_user'),
    path('moderation_dashboard/', views.moderation_dashboard, name='moderation_dashboard'),
 
    path('notifications/', notifications, name='notifications'),
    path('notifications/read/<int:notification_id>/', mark_as_read, name='mark_as_read'),
]


