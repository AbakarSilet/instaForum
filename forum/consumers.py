# forum/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ThreadConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.slug = self.scope['url_route']['kwargs']['slug']
        self.group_name = f'thread_{self.slug}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def thread_liked(self, event):
        # Quand le serveur envoie un événement
        await self.send(text_data=json.dumps({
            'slug': event['slug'],
            'likes_count': event['likes_count'],
        }))
