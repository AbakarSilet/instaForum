from rest_framework import serializers
from .models import Event, Attendee
from django.contrib.auth import get_user_model

User = get_user_model()

class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.ReadOnlyField(source='organizer.username')
    
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'location', 'date', 'organizer', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'organizer', 'created_at', 'updated_at']

class AttendeeSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Attendee
        fields = ['id', 'user', 'event', 'registered_at']

    def get_user(self, obj):
        return {
            "username": obj.user.username,
            "profile_image": obj.user.profile_image.url if obj.user.profile_image else None,
        }
