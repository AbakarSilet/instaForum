
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path('forum/', include('forum.urls')),
    path('news/', include('news.urls')),
    path('resources/', include('resources.urls')),
    path('events/', include('events.urls')),
    path('messaging/', include('messaging.urls')),
    path('accounts/', include('modelUser.urls')),
    path('',include('home.urls')),
    path('accounts/', include('allauth.urls')),
    # path('__debug__/', include('debug_toolbar.urls')),
)

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

