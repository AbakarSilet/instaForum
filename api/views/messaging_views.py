from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q, Max, Count
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from allauth.account.decorators import verified_email_required
from django.utils.decorators import method_decorator
from messaging.serializers import MessageSerializer, ConversationSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework import status
from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation

User = get_user_model()
from messaging.exceptions import *
from messaging.models import Message
from messaging.serializers import MessageSerializer, ConversationSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    
    def perform_create(self, serializer):
        try:
            serializer.save(sender=self.request.user)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        
    def handle_exception(self, exc):
        if isinstance(exc, MessagingException):
            return Response(
                {'error': exc.message, 'code': exc.code},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().handle_exception(exc)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            raise UnauthorizedAccessException(
                "Authentication required",
                code="authentication_required"
            )
        return Message.objects.select_related('sender', 'receiver').filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        ).order_by('-created_at')

    @swagger_auto_schema(
        responses={
            200: ConversationSerializer(many=True),
            401: "Authentication required",
            403: "Email verification required"
        }
    )
    @action(detail=False, methods=['GET'])
    def conversations(self, request):
        try:
            if not request.user.is_authenticated:
                raise UnauthorizedAccessException(
                    "Authentication required",
                    code="authentication_required"
                )
            # Vérifier si l'email est vérifié
            email_address = EmailAddress.objects.filter(user=request.user, verified=True).first()
            if not email_address:
                # Envoyer un email de vérification
                send_email_confirmation(request, request.user)
                return Response(
                    {
                        'error': 'Email verification required',
                        'code': 'email_not_verified',
                        'message': 'A verification email has been sent to your email address'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            conversations = (
                Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
                .values('sender', 'receiver')
                .annotate(last_message_date=Max('created_at'))
                .order_by('-last_message_date')
            )

            # Optimiser pour éviter les requêtes N+1
            conversation_data = []
            seen_users = set()

            for conv in conversations:
                other_user_id = conv['receiver'] if conv['sender'] == request.user.id else conv['sender']
                
                if other_user_id not in seen_users:
                    seen_users.add(other_user_id)
                    
                    try:
                        last_message = Message.objects.filter(
                            Q(sender_id__in=[request.user.id, other_user_id]),
                            Q(receiver_id__in=[request.user.id, other_user_id])
                        ).select_related('sender', 'receiver').latest('created_at')

                        unread_count = Message.objects.filter(
                            sender_id=other_user_id,
                            receiver_id=request.user.id,
                            is_read=False
                        ).count()

                        conversation_data.append({
                            'user': last_message.sender if last_message.sender != request.user else last_message.receiver,
                            'last_message': last_message,
                            'unread_count': unread_count,
                            'last_message_date': conv['last_message_date']
                        })
                    except Message.DoesNotExist:
                        continue

            serializer = ConversationSerializer(conversation_data, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e), 'code': 'server_error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    @action(detail=False, methods=['GET'])
    def thread(self, request):
        """
        URL: /api/messaging/thread/?user_id=123
        Récupère tous les messages entre l'utilisateur connecté et l'utilisateur spécifié
        """
        try:
            if not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentication required', 'code': 'authentication_required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Vérifier si l'email est vérifié
            email_address = EmailAddress.objects.filter(user=request.user, verified=True).first()
            if not email_address:
                # Envoyer un email de vérification
                send_email_confirmation(request, request.user)
                return Response(
                    {
                        'error': 'Email verification required',
                        'code': 'email_not_verified',
                        'message': 'A verification email has been sent to your email address'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            user_id = request.query_params.get('user_id')
            if not user_id:
                return Response(
                    {'error': 'user_id parameter is required', 'code': 'missing_user_id'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            other_user = get_object_or_404(User, id=user_id)

            # Récupérer les messages de la conversation
            messages = Message.objects.select_related('sender', 'receiver').filter(
                Q(sender=request.user, receiver=other_user) |
                Q(sender=other_user, receiver=request.user)
            ).order_by('created_at')

            # Marquer les messages comme lus
            messages.filter(
                sender=other_user,
                receiver=request.user,
                is_read=False
            ).update(is_read=True, read_at=timezone.now())

            serializer = MessageSerializer(messages, many=True)
            return Response({
                'thread_id': f"{min(request.user.id, other_user.id)}_{max(request.user.id, other_user.id)}",
                'other_user': UserSerializer(other_user).data,
                'messages': serializer.data
            })

        except Exception as e:
            return Response(
                {'error': str(e), 'code': 'server_error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['POST'])
    def mark_as_read(self, request):
        message_ids = request.data.get('message_ids', [])
        if not message_ids:
            return Response(
                {"error": "message_ids are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        messages = Message.objects.filter(
            id__in=message_ids,
            receiver=request.user,
            is_read=False
        )
        messages.update(is_read=True, read_at=timezone.now())
        return Response({"status": "messages marked as read"})
    
class UserSearchAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        return User.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query),
            is_active=True
        ).exclude(id=self.request.user.id)

class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all().order_by('first_name')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

