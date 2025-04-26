from rest_framework_simplejwt.views import TokenRefreshView

from api.views import messaging_views, news_views
from .views.user_views import (
    GoogleLogin,
    PasswordResetAPIView,
    PasswordResetConfirmAPIView,
    UserProfileUpdateView,
    UserRegisterAPIView,
    UserLoginView,
    UserProfileAPIView,
    PasswordChangeAPIView,
    UserLogoutView,
    get_user_groups,
    
)
from django.http import HttpResponse
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.forum_views import (CategoryViewSet, NotificationViewSet, ReportAPIView, SubforumViewSet, ThreadViewSet,
                         PostViewSet, ReportView,UserPublicProfileView)

from .views import events_views


# URLs pour le forum

forum_urlpatterns= [
    # Catégories
    path('categories/', CategoryViewSet.as_view({'get': 'list'}), name='category-list'),
    path('categories/<int:pk>/', CategoryViewSet.as_view({'get': 'retrieve'}), name='category-detail'),
    path('categories/<int:pk>/subforums/', CategoryViewSet.as_view({'get': 'subforums'}), name='category-subforums'),
    # Sous-forums
    path('subforums/', SubforumViewSet.as_view({'get': 'list'}), name='subforum-list'),
    path('subforums/<str:slug>/', SubforumViewSet.as_view({'get': 'retrieve'}), name='subforum-detail'),
    path('subforums/<str:slug>/threads/', SubforumViewSet.as_view({'get': 'threads'}), name='subforum-threads'),
    # Threads
    path('threads/', ThreadViewSet.as_view({'get': 'list', 'post': 'create'}), name='thread-list'),
    path('threads/<str:slug>/', ThreadViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='thread-detail'),
    path('threads/<str:slug>/posts/', ThreadViewSet.as_view({'get': 'posts'}), name='thread-posts'),
    path('threads/<str:slug>/like/', ThreadViewSet.as_view({'post': 'like'}), name='thread-like'),
    path('threads/<str:slug>/close/', ThreadViewSet.as_view({'post': 'close'}), name='thread-close'),
    path('threads/<str:slug>/open/', ThreadViewSet.as_view({'post': 'open'}), name='thread-open'),
    path('threads/<str:slug>/toggle_close/', ThreadViewSet.as_view({'post': 'toggle_close'}), name='thread-toggle-close'),
    # Posts
    path('posts/', PostViewSet.as_view({'get': 'list', 'post': 'create'}), name='post-list'),
    path('posts/<int:pk>/like/', PostViewSet.as_view({'post': 'like'}), name='post-like'),
    path('posts/<int:pk>/', PostViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='post-detail'),
    # Signalements
    path('report/', ReportView.as_view(), name='report'),
    # Profils utilisateurs (si cette vue est dans l'app forum)
    path('users/<str:username>/', UserPublicProfileView.as_view(), name='user-public-profile'),
    
    #Signalement
    path('report/thread/<slug:thread_slug>/', ReportAPIView.as_view(), name='report-thread'),
    path('report/post/<int:post_id>/', ReportAPIView.as_view(), name='report-post'),
    path('report/users/<str:username>/', ReportAPIView.as_view(), name='report-user'),

    
    # Notifications
    path('notifications/', NotificationViewSet.as_view({'get': 'list'}), name='notification-list'),
    path('notifications/unread/', NotificationViewSet.as_view({'get': 'unread'}), name='notification-unread'),
    path('notifications/<int:pk>/mark-as-read/', NotificationViewSet.as_view({'post': 'mark_as_read'}), name='notification-mark-as-read'),
    path('notifications/mark-all-as-read/', NotificationViewSet.as_view({'post': 'mark_all_as_read'}), name='notification-mark-all-as-read'),
    path('notifications/count-unread/', NotificationViewSet.as_view({'get': 'count_unread'}), name='notification-count-unread'),

]

# URLs pour les utilisateurs et l'authentification
user_urlpatterns = [
    path('all-users/', messaging_views.UserListView.as_view(), name='user-list'),
    path('auth/register/', UserRegisterAPIView.as_view(), name='register'),
    path('auth/login/', UserLoginView.as_view(), name='login'),
    path('auth/logout/', UserLogoutView.as_view(), name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('profile/', UserProfileAPIView.as_view(), name='user_profile'),
    path('profile/edit/', UserProfileUpdateView.as_view(), name='profile-update'),
    path('password/change/', PasswordChangeAPIView.as_view(), name='password_change'),
    path('auth/password/reset/', PasswordResetAPIView.as_view(),name='password_reset'),
    path('auth/password/reset/confirm/<str:uidb36>/<str:key>/', PasswordResetConfirmAPIView.as_view(), name='password_reset_confirm'),
    path('auth/groups/', get_user_groups, name='user-groups'),
]

events_urlpatterns = [
    path('list/', events_views.EventListAPIView.as_view(), name='event-list'),
    path('create/', events_views.EventCreateAPIView.as_view(), name='event-create'),
    path('detail/<int:pk>/', events_views.EventDetailAPIView.as_view(), name='event-detail'),
    path('delete/<int:event_id>/', events_views.DeleteEventAPIView.as_view(), name='delete-event'),
    path('participate/<int:event_id>/', events_views.ParticipateEventAPIView.as_view(), name='participate-event'),
    path('<int:event_id>/attendees/', events_views.EventAttendeesAPIView.as_view(), name='event-attendees'),
]

news_urlpatterns = [
    path('articles/', news_views.NewsArticleViewSet.as_view({'get': 'list'}), name='articles-list'),
    path('sources/', news_views.NewsSourceViewSet.as_view({'get': 'list'}), name='sources-news'),
    ]

messaging_urlpatterns = [
    
    path('conversations/', messaging_views.MessageViewSet.as_view({'get': 'conversations'}), name='message-conversations'),
    path('thread/', messaging_views.MessageViewSet.as_view({'get': 'thread'}), name='message-thread'),
    path('messages/', messaging_views.MessageViewSet.as_view({'post': 'create'}), name='message-create'),
    path('mark_as_read/', messaging_views.MessageViewSet.as_view({'post': 'mark_as_read'}),  name='message-mark-read'),
    path('users/search/', messaging_views.UserSearchAPIView.as_view(),  name='user-search')
    
]

from django.urls import path
from .views.resources_views import (
    ResourceListAPIView,
    ImageResourceCreateAPIView,
    LinkResourceCreateAPIView,
    DocumentResourceCreateAPIView,
    VideoResourceCreateAPIView,
    ResourceDetailAPIView,
    ResourceSearchAPIView,
)

resource_urlpatterns = [
    path('list/', ResourceListAPIView.as_view(), name='resource-list'),
    path('create/image/', ImageResourceCreateAPIView.as_view(), name='image-resource-create'),
    path('create/link/', LinkResourceCreateAPIView.as_view(), name='link-resource-create'),
    path('create/document/', DocumentResourceCreateAPIView.as_view(), name='document-resource-create'),
    path('create/video/', VideoResourceCreateAPIView.as_view(), name='video-resource-create'),
    path('detail/<int:pk>/', ResourceDetailAPIView.as_view(), name='resource-detail'),
    path('search/', ResourceSearchAPIView.as_view(), name='resource-search'), 
]

urlpatterns = [
    path('forum/', include(forum_urlpatterns)),  # URL du forum
    path('user/', include(user_urlpatterns)),    # URL des utilisateurs
    path('events/', include(events_urlpatterns)), # URL des événements
    path('news/', include(news_urlpatterns)),    # URL des news
    path('resources/', include(resource_urlpatterns)),  # URL des ressources
    path('messaging/', include(messaging_urlpatterns)),  # URL des messages
]






