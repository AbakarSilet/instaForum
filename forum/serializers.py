from rest_framework import serializers
from django.db import transaction

from forum.utils import normalize_tags, remove_accents
from .models import (Category, Subforum, Thread, Post, Report, Like, 
                    Dislike, Badge, UserBadge, Notification)
from taggit.serializers import TagListSerializerField, TaggitSerializer
from modelUser.serializers import UserSerializer
from modelUser.models import User 

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ['id', 'name', 'description', 'icon']
        read_only_fields = fields

class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)
    
    class Meta:
        model = UserBadge
        fields = ['id', 'badge', 'awarded_at']
        read_only_fields = fields

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'description', 'slug']
        read_only_fields = fields

class SubforumSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    image = serializers.ImageField(required=False)  # Make image optional
    
    class Meta:
        model = Subforum
        fields = ['id', 'category', 'title', 'description', 'slug', 
                 'view_count', 'image']
        read_only_fields = ['id', 'slug', 'view_count']

class ThreadListSerializer(TaggitSerializer, serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagListSerializerField(required=False) 
    image = serializers.ImageField(required=False) 
    post_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = ['id', 'subforum', 'author', 'title', 'image', 'content', 'slug',
                 'created_at', 'updated_at', 'view_count', 'tags', 'is_closed',
                 'post_count', 'like_count', 'is_liked', 'likes']
        read_only_fields = ['id', 'slug', 'view_count', 'created_at', 
                          'updated_at', 'likes']

    def get_post_count(self, obj):
        return obj.posts.count()

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

class ThreadCreateSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False, allow_empty=True)
    image = serializers.ImageField(required=False)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Thread
        fields = ['id', 'subforum', 'title', 'content', 'image', 'tags', 
                 'slug', 'author', 'created_at', 'updated_at', 'is_closed']
        read_only_fields = ['id', 'slug', 'author', 'created_at', 'updated_at', 'likes']

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', []) 
        normalized_tags = [remove_accents(tag) for tag in tags_data]
        thread = Thread.objects.create(**validated_data)
        thread.tags.add(*normalized_tags)
        return thread

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='author', 
        write_only=True,
        required=False
    )
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'thread', 'author', 'author_id', 'content', 'created_at', 
                 'updated_at', 'likes', 'like_count', 'is_liked']
        read_only_fields = ['id', 'created_at', 'updated_at', 'author', 'likes']
    
    def get_like_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
    
class UserPublicProfileSerializer(serializers.ModelSerializer):
    badges = serializers.SerializerMethodField()
    threads = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username','first_name','last_name', 'profile_image', 'badges', 'threads']
        read_only_fields = fields

    def get_badges(self, obj):
        user_badges = UserBadge.objects.filter(user=obj)
        return UserBadgeSerializer(user_badges, many=True).data

    def get_threads(self, obj):
        threads = Thread.objects.filter(author=obj)
        return ThreadListSerializer(threads, many=True).data


class ReportSerializer(serializers.ModelSerializer):
    reported_by = UserSerializer(read_only=True)

    class Meta:
        model = Report
        fields = ['id', 'reported_by', 'report_type', 'report_reason',
                 'thread', 'post', 'reported_user', 'created_at']
        read_only_fields = ['id', 'created_at', 'reported_by']

    def validate(self, data):
        """
        Vérifie qu'un seul élément (thread, post ou user) est signalé à la fois
        """
        reported_items = [
            bool(data.get('thread')),
            bool(data.get('post')),
            bool(data.get('reported_user'))
        ]
        
        if sum(reported_items) != 1:
            raise serializers.ValidationError(
                "Un seul élément (thread, post ou utilisateur) doit être signalé"
            )

        if not data.get('report_reason'):
            raise serializers.ValidationError(
                "La raison du signalement est obligatoire"
            )

        if len(data.get('report_reason')) < 10:
            raise serializers.ValidationError(
                "La raison du signalement doit contenir au moins 10 caractères"
            )

        return data

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'thread', 'created_at']
        read_only_fields = ['id', 'created_at']

class DislikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dislike
        fields = ['id', 'user', 'thread', 'created_at']
        read_only_fields = ['id', 'created_at']

class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='user', 
        write_only=True
    )

    class Meta:
        model = Notification
        fields = ['id', 'user', 'user_id', 'message', 'created_at', 'is_read', 'link']
        read_only_fields = ['id', 'created_at']