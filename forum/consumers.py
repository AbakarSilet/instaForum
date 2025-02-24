import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Thread, Post
from django.template.defaultfilters import date as date_filter

class ThreadConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.thread_slug = self.scope['url_route']['kwargs']['thread_slug']
        self.room_group_name = f'thread_{self.thread_slug}'

        # Rejoindre le groupe de la room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Quitter le groupe de la room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'new_post':
            post_data = text_data_json.get('post')
            # Traiter le nouveau post
            post = await self.save_post(post_data)
            if post:
                # Envoyer le message au groupe
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'post_message',
                        'post': {
                            'id': post.id,
                            'content': post.content,
                            'author_name': f"{post.author.first_name} {post.author.last_name}",
                            'author_image': post.author.profile_image.url if post.author.profile_image else None,
                            'created_at': date_filter(post.created_at, "d M H:i"),
                            'tags': [tag.name for tag in post.tags.all()]
                        }
                    }
                )

    async def post_message(self, event):
        post = event['post']
        
        # Envoyer le message au WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new_post',
            'post': post
        }))

    @database_sync_to_async
    def save_post(self, post_data):
        try:
            thread = Thread.objects.get(slug=self.thread_slug)
            post = Post.objects.create(
                thread=thread,
                author_id=post_data['author_id'],
                content=post_data['content']
            )
            
            # Gérer les tags
            if 'tags' in post_data:
                post.tags.add(*post_data['tags'])
            
            return post
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du post: {e}")
            return None