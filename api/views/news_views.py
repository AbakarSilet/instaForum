# news/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from news.models import NewsSource, NewsArticle
from news.serializers import NewsSourceSerializer, NewsArticleSerializer
from django.db.models import F
from rest_framework.permissions import AllowAny

class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = NewsArticle.objects.filter(is_active=True)
    serializer_class = NewsArticleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category', None)
        source = self.request.query_params.get('source', None)

        if category:
            queryset = queryset.filter(category=category)
        if source:
            queryset = queryset.filter(source__name=source)

        return queryset

    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        article = self.get_object()
        article.views_count = F('views_count') + 1
        article.save()
        return Response({'status': 'views incremented'})

class NewsSourceViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = NewsSource.objects.all()
    serializer_class = NewsSourceSerializer
