from django.http import Http404
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from django.db.models import F
from django.db import transaction
from django.db.utils import IntegrityError
from forum.models import (Category, Notification, Subforum, Thread, Post, Report, 
                         Like, Dislike, Badge, UserBadge)
from forum.serializers import (CategorySerializer, NotificationSerializer, SubforumSerializer, 
                             ThreadListSerializer, ThreadCreateSerializer,
                             PostSerializer, ReportSerializer, 
                             BadgeSerializer, UserBadgeSerializer,
                             UserPublicProfileSerializer)
from forum.utils import normalize_tags
from modelUser.models import User as USER

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True)
    def subforums(self, request, pk=None):
        category = self.get_object()
        subforums = category.subforums.all()
        serializer = SubforumSerializer(subforums, many=True)
        return Response(serializer.data)

class SubforumViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subforum.objects.all()
    serializer_class = SubforumSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    @action(detail=True)
    def threads(self, request, slug=None):
        subforum = self.get_object()
        threads = subforum.threads.all().order_by('-created_at')
        serializer = ThreadListSerializer(threads, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count = F('view_count') + 1
        instance.save()
        return super().retrieve(request, *args, **kwargs)

class ThreadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        return Thread.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return ThreadCreateSerializer
        return ThreadListSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        print(f"Received data: {self.request.data}") 
        try:
            with transaction.atomic():
                
                thread = serializer.save(author=self.request.user)
                return thread
        except IntegrityError as e:
            raise ValidationError({
                'detail': 'Erreur lors de la création du thread. Veuillez réessayer.'
            })
            
    @action(detail=True)
    def posts(self, request, slug=None):
        thread = self.get_object()
        posts = thread.posts.all().order_by('created_at')
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def like(self, request, slug=None):
        thread = self.get_object()
        user = request.user
        
        if thread.likes.filter(id=user.id).exists():
            thread.likes.remove(user)
            return Response({'status': 'unliked'})
        else:
            thread.likes.add(user)
            return Response({'status': 'liked'})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count = F('view_count') + 1
        instance.save()
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def close(self, request, slug=None):
        thread = self.get_object()
        if thread.author != request.user:
            return Response(
                {'detail': "Vous n'êtes pas l'auteur de ce thread."},
                status=status.HTTP_403_FORBIDDEN
            )
        thread.is_closed = True
        thread.save()
        return Response(
            {'status': 'thread fermé', 'is_closed': True},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def open(self, request, slug=None):
        thread = self.get_object()
        if thread.author != request.user:
            return Response(
                {'detail': "Vous n'êtes pas l'auteur de ce thread."},
                status=status.HTTP_403_FORBIDDEN
            )
        thread.is_closed = False
        thread.save()
        return Response(
            {'status': 'thread ouvert', 'is_closed': False},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_close(self, request, slug=None):
        thread = self.get_object()
        if thread.author != request.user:
            return Response(
                {'detail': "Vous n'êtes pas l'auteur de ce thread."},
                status=status.HTTP_403_FORBIDDEN
            )
        thread.is_closed = not thread.is_closed
        thread.save()
        return Response(
            {
                'status': 'thread fermé' if thread.is_closed else 'thread ouvert',
                'is_closed': thread.is_closed
            },
            status=status.HTTP_200_OK
        )

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Post.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        # Utiliser l'utilisateur connecté comme auteur
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        
        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            return Response({'status': 'unliked'})
        else:
            post.likes.add(user)
            return Response({'status': 'liked'})      

class ReportView(generics.CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)

# Bonne
class UserPublicProfileView(generics.RetrieveAPIView):
    serializer_class = UserPublicProfileSerializer
    queryset = USER.objects.all()
    lookup_field = 'username'
    
class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Récupère uniquement les notifications non lues de l'utilisateur connecté
        return Notification.objects.filter(user=self.request.user, is_read=False).order_by('-created_at')

    def perform_create(self, serializer):
        # Assure que l'utilisateur connecté est défini comme l'utilisateur de la notification
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['GET'])
    def unread(self, request):
        # Récupère uniquement les notifications non lues
        unread_notifications = self.get_queryset()
        serializer = self.get_serializer(unread_notifications, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def mark_as_read(self, request, pk=None):
        # Marque une notification spécifique comme lue
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def mark_all_as_read(self, request):
        # Marque toutes les notifications comme lues
        unread_notifications = self.get_queryset()
        unread_notifications.update(is_read=True)
        return Response({'status': 'all notifications marked as read'})

    @action(detail=False, methods=['GET'])
    def count_unread(self, request):
        # Compte les notifications non lues
        count = self.get_queryset().count()
        return Response({'unread_count': count})

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

class ReportAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReportSerializer

    def get_reported_item(self, request, **kwargs):
        """Helper method to get the reported item based on URL"""
        path = request.path
        
        if 'report/thread' in path:
            thread_slug = kwargs.get('thread_slug')
            return get_object_or_404(Thread, slug=thread_slug), 'thread'
        
        elif 'report/post' in path:
            post_id = kwargs.get('post_id')
            return get_object_or_404(Post, id=post_id), 'post'
        
        elif 'report/users' in path:
            username = kwargs.get('username')
            return get_object_or_404(get_user_model(), username=username), 'user'
        
        return None, None

    def post(self, request, *args, **kwargs):
        # Vérifie les champs obligatoires
        if not request.data.get('report_type') or not request.data.get('report_reason'):
            return Response(
                {'error': 'Les champs report_type et report_reason sont obligatoires'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifie si report_type est valide
        if request.data.get('report_type') not in dict(Report.REPORT_CHOICES):
            return Response(
                {'error': 'Type de signalement invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Récupère l'élément signalé et son type
        try:
            reported_item, item_type = self.get_reported_item(request, **kwargs)
        except Http404:
            return Response(
                {'error': 'Élément non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not reported_item:
            return Response(
                {'error': 'Type d\'élément invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Empêche l'utilisateur de se signaler lui-même
        if item_type == 'user' and reported_item == request.user:
            return Response(
                {'error': 'Vous ne pouvez pas vous signaler vous-même'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prépare les données pour le serializer
        report_data = {
            'report_type': request.data.get('report_type'),
            'report_reason': request.data.get('report_reason'),
            'reported_by': request.user.id
        }

        # Ajoute l'élément signalé approprié
        if item_type == 'thread':
            report_data['thread'] = reported_item.id
        elif item_type == 'post':
            report_data['post'] = reported_item.id
        else:  # user
            report_data['reported_user'] = reported_item.id

        serializer = self.serializer_class(data=report_data)
        
        if serializer.is_valid():
            serializer.save(reported_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

