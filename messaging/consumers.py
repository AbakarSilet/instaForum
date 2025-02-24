import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message
from django.utils import timezone
from django.utils.timesince import timesince
from django.db.models import Q

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.other_username = self.scope['url_route']['kwargs']['username']
        
        # Rejoindre le groupe personnel de l'utilisateur pour les mises à jour de la sidebar
        self.personal_group = f'user_{self.user.username}'
        await self.channel_layer.group_add(
            self.personal_group,
            self.channel_name
        )
        
        # Groupe pour la conversation spécifique
        users = sorted([self.user.username, self.other_username])
        self.room_group_name = f'chat_{users[0]}_{users[1]}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            self.personal_group,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        # Vérifier si la clé 'message' existe
        if 'message' not in text_data_json:
            return  # ou gérer l'erreur d'une autre manière
            
        message = text_data_json['message']
        
        # Sauvegarder le message
        message_object = await self.save_message(message)
        
        # Obtenir les informations de la conversation mise à jour
        conversation_info = await self.get_conversation_info(self.other_username)
        
        # Envoyer le message dans la conversation
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_username': self.user.username,
                'timestamp': message_object.created_at.isoformat(),
            }
        )

        # Envoyer la mise à jour de la sidebar aux deux utilisateurs
        for username in [self.user.username, self.other_username]:
            await self.channel_layer.group_send(
                f'user_{username}',
                {
                    'type': 'update_sidebar',
                    'conversation': conversation_info
                }
            )
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message'],
            'sender_username': event['sender_username'],
            'timestamp': event['timestamp'],
        }))

    async def update_sidebar(self, event):
        await self.send(text_data=json.dumps({
            'type': 'update_sidebar',
            'conversation': event['conversation']
        }))

    @database_sync_to_async
    def save_message(self, content):
        other_user = User.objects.get(username=self.other_username)
        return Message.objects.create(
            sender=self.user,
            receiver=other_user,
            content=content
        )

    @database_sync_to_async
    def get_conversation_info(self, username):
        other_user = User.objects.get(username=username)
        last_message = Message.objects.filter(
            Q(sender=self.user, receiver=other_user) |
            Q(sender=other_user, receiver=self.user)
        ).latest('created_at')

        unread_count = Message.objects.filter(
            sender=other_user,
            receiver=self.user,
            is_read=False
        ).count()

        return {
            'username': other_user.username,
            'first_name': other_user.first_name,
            'last_name': other_user.last_name,
            'profile_image_url': other_user.profile_image.url if other_user.profile_image else '',
            'last_message': last_message.content,
            'last_message_date': timesince(last_message.created_at),
            'unread_count': unread_count
        }
    
    