from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/thread/(?P<thread_slug>[\w-]+)/$', consumers.ThreadConsumer.as_asgi()),
]