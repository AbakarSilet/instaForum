from rest_framework import serializers
from .models import Resource



class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'title', 'description', 'resource_type', 'image', 'link', 'file', 'video', 'date_added']
        read_only_fields = ['resource_type', 'date_added']


class ImageResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'title', 'description', 'resource_type', 'image', 'date_added']
        read_only_fields = ['resource_type', 'date_added']
        extra_kwargs = {
            'resource_type': {'default': 'image'},
        }

class LinkResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'title', 'description', 'resource_type', 'link', 'date_added']
        read_only_fields = ['resource_type', 'date_added']
        extra_kwargs = {
            'resource_type': {'default': 'link'},
        }

class DocumentResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'title', 'description', 'resource_type', 'file', 'date_added']
        read_only_fields = ['resource_type', 'date_added']
        extra_kwargs = {
            'resource_type': {'default': 'document'},
        }

class VideoResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'title', 'description', 'resource_type', 'video', 'date_added']
        read_only_fields = ['resource_type', 'date_added']
        extra_kwargs = {
            'resource_type': {'default': 'video'},
        }
