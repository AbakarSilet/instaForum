from django.urls import re_path
from . import consumers
import  forum.consumers as cons

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<username>\w+)/$', consumers.ChatConsumer.as_asgi()),
    
    re_path(r'ws/forum/threads/(?P<slug>[\w-]+)/$', cons.ThreadConsumer.as_asgi()),
]