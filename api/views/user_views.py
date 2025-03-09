

from tokenize import TokenError
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework import  status, generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth import get_user_model, logout,authenticate
from modelUser.serializers import (
    PasswordResetSerializer,
    UserSerializer, 
    UserRegisterSerializer, 
    PasswordChangeSerializer,
    UserProfileUpdateSerializer
)
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from modelUser.exceptions import *
from allauth.account.utils import complete_signup
from django.utils.translation import gettext as _
from allauth.account.utils import url_str_to_user_pk
from allauth.account.forms import ResetPasswordKeyForm
from allauth.account import app_settings

User = get_user_model()

class UserRegisterAPIView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            if not serializer.is_valid():
                raise BadRequestError(detail=serializer.errors)

            user = serializer.save()
            
            # Utilise le système de verification d'allauth
            complete_signup(request, user, app_settings.EMAIL_VERIFICATION, None)
            
            return Response({
                'detail': 'Compte créé avec succès. Veuillez vérifier votre email pour confirmer votre email.',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
            
        except serializers.ValidationError as e:
            raise BadRequestError(detail=e.detail)
        except Exception as e:
            raise BadRequestError(detail=str(e))


class UserLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            raise BadRequestError(
                detail='Veuillez fournir un nom d\'utilisateur ou email et un mot de passe.'
            )

        user = authenticate(request, username=username, password=password)
        
        if not user:
            raise UnauthorizedError(detail='Identifiants invalides.')
            
        if not user.is_active:
            raise ForbiddenError(detail='Ce compte a été désactivé.')

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })


class UserProfileUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileUpdateSerializer

    def get_object(self):
        try:
            return self.request.user
        except User.DoesNotExist:
            raise NotFoundError(detail="Utilisateur non trouvé")
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if not serializer.is_valid():
            raise BadRequestError(detail=serializer.errors)
            
        try:
            self.perform_update(serializer)
            return Response(UserSerializer(instance).data)
        except Exception as e:
            raise BadRequestError(
                detail='Une erreur est survenue lors de la mise à jour du profil.'
            )


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = PasswordChangeSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': ['Ancien mot de passe incorrect.']},
                    status=status.HTTP_400_BAD_REQUEST
                )

            new_password = serializer.validated_data['new_password1']

            try:
                validate_password(new_password, user)
            except ValidationError as e:
                return Response(
                    {'new_password1': e.messages},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(new_password)
            user.save()

            return Response(
                {'detail': 'Mot de passe modifié avec succès.'},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PasswordResetAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Envoie l'email de réinitialisation
            success = serializer.save(request)
            
            if success:
                return Response(
                    {
                        'detail': 'Instructions de réinitialisation du mot de passe '
                                 'envoyées à votre adresse email.'
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        'detail': 'Une erreur est survenue lors de l\'envoi de l\'email.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PasswordResetConfirmAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb36, key, *args, **kwargs):
        try:
            # Récupère l'utilisateur à partir de l'uidb36
            user_pk = url_str_to_user_pk(uidb36)
            user = User.objects.get(pk=user_pk)
            
            # Prépare les données pour le formulaire
            data = {
                'uid': uidb36,
                'key': key,
                'password1': request.data.get('new_password1'),
                'password2': request.data.get('new_password2'),
            }

            form = ResetPasswordKeyForm(user=user, data=data)
            if form.is_valid():
                form.save()
                return Response(
                    {'detail': 'Mot de passe réinitialisé avec succès.'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    form.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

        except (TypeError, ValueError, User.DoesNotExist) as e:
            return Response(
                {'detail': 'Lien de réinitialisation invalide.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({
                    'error': 'Le token de rafraîchissement est requis'
                }, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()
            logout(request)
            return Response({'detail': 'Déconnexion réussie.'})
        except TokenError:
            return Response({
                'error': 'Token invalide ou expiré'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Une erreur est survenue lors de la déconnexion',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:8000/accounts/google/login/callback/"
    client_class = OAuth2Client


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_groups(request):
    groups = request.user.groups.all()
    group_names = [group.name for group in groups]
    return Response({'groups': group_names})