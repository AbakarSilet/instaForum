from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_image']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    receiver_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'receiver_id', 'content', 
                 'created_at', 'is_read', 'read_at']
        read_only_fields = ['is_read', 'read_at']

    def validate_receiver_id(self, value):
        try:
            receiver = User.objects.get(id=value)
            if not receiver.is_active:
                raise serializers.ValidationError("Cet utilisateur n'est plus actif.")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Utilisateur introuvable.")

    def create(self, validated_data):
        receiver_id = validated_data.pop('receiver_id')
        receiver = User.objects.get(id=receiver_id)
        message = Message.objects.create(
            receiver=receiver,
            **validated_data
        )
        return message

class ConversationSerializer(serializers.Serializer):
    user = UserSerializer()
    last_message = MessageSerializer()
    unread_count = serializers.IntegerField()
    last_message_date = serializers.DateTimeField()
    