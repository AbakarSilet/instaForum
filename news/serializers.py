# news/serializers.py
from rest_framework import serializers
from .models import NewsSource, NewsArticle

class NewsSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsSource
        fields = ['id', 'name', 'url']

class NewsArticleSerializer(serializers.ModelSerializer):
    source = NewsSourceSerializer(read_only=True)
    time_since_published = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = [
            'id', 'title', 'description', 'url', 'image_url',
            'source', 'published_at', 'category', 'views_count',
            'time_since_published'
        ]

    def get_time_since_published(self, obj):
        from django.utils import timezone
        from datetime import datetime
        now = timezone.now()
        time_diff = now - obj.published_at

        if time_diff.days > 0:
            return f"il y a {time_diff.days} jour{'s' if time_diff.days > 1 else ''}"
        elif time_diff.seconds >= 3600:
            hours = time_diff.seconds // 3600
            return f"il y a {hours} heure{'s' if hours > 1 else ''}"
        else:
            minutes = time_diff.seconds // 60
            return f"il y a {minutes} minute{'s' if minutes > 1 else ''}"
        

# from rest_framework import serializers
# from .models import NewsSource, NewsArticle

# class NewsSourceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = NewsSource
#         fields = ['id', 'name', 'url']

# class NewsArticleListSerializer(serializers.ModelSerializer):
#     source_name = serializers.CharField(source='source.name', read_only=True)
    
#     class Meta:
#         model = NewsArticle
#         fields = [
#             'id', 
#             'title', 
#             'description', 
#             'url', 
#             'image_url',
#             'source_name',
#             'published_at',
#             'category',
#             'views_count'
#         ]

# class NewsArticleDetailSerializer(serializers.ModelSerializer):
#     source = NewsSourceSerializer(read_only=True)
    
#     class Meta:
#         model = NewsArticle
#         fields = [
#             'id', 
#             'title', 
#             'description', 
#             'url', 
#             'image_url',
#             'source',
#             'published_at',
#             'created_at',
#             'category',
#             'views_count',
#             'is_active'
#         ]