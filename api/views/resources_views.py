from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db import transaction
from resources.models import Resource
from resources.serializers import (
    ResourceSerializer,
    ImageResourceSerializer,
    LinkResourceSerializer,
    DocumentResourceSerializer,
    VideoResourceSerializer
)

class BaseResourceCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if not self.request.user.groups.filter(name='Teacher').exists():
            raise PermissionDenied("Seuls les enseignants peuvent créer des ressources.")
        
        try:
            with transaction.atomic():
                serializer.save(user=self.request.user, resource_type=self.resource_type)
        except ValidationError as e:
            raise ValidationError(detail={'error': str(e)})
        except Exception as e:
            raise ValidationError(detail={'error': "Une erreur s'est produite lors de la création de la ressource."})

class ResourceListAPIView(generics.ListAPIView):
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return Resource.objects.select_related('user').order_by('-date_added')

class ImageResourceCreateAPIView(BaseResourceCreateAPIView):
    queryset = Resource.objects.filter(resource_type='image')
    serializer_class = ImageResourceSerializer
    resource_type = 'image'

class LinkResourceCreateAPIView(BaseResourceCreateAPIView):
    queryset = Resource.objects.filter(resource_type='link')
    serializer_class = LinkResourceSerializer
    resource_type = 'link'

class DocumentResourceCreateAPIView(BaseResourceCreateAPIView):
    queryset = Resource.objects.filter(resource_type='document')
    serializer_class = DocumentResourceSerializer
    resource_type = 'document'

class VideoResourceCreateAPIView(BaseResourceCreateAPIView):
    queryset = Resource.objects.filter(resource_type='video')
    serializer_class = VideoResourceSerializer
    resource_type = 'video'

class ResourceDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return Resource.objects.select_related('user')

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user and not request.user.is_staff:
            raise PermissionDenied("Vous n'avez pas la permission de modifier cette ressource.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user and not request.user.is_staff:
            raise PermissionDenied("Vous n'avez pas la permission de supprimer cette ressource.")
        return super().destroy(request, *args, **kwargs)

class ResourceSearchAPIView(generics.ListAPIView):
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        query = self.request.query_params.get('q', '').strip()
        if not query:
            return Resource.objects.none()

        try:
            search_vector = SearchVector('title', 'description', 'resource_type')
            search_query = SearchQuery(query)

            q_objects = Q(title__icontains=query) | \
                       Q(description__icontains=query) | \
                       Q(resource_type__icontains=query)

            return Resource.objects.select_related('user').annotate(
                rank=SearchRank(search_vector, search_query)
            ).filter(
                Q(rank__gte=0.01) | q_objects
            ).order_by('-rank', '-date_added')

        except Exception as e:
            raise ValidationError(detail={'error': "Une erreur s'est produite lors de la recherche."})