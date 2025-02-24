# modelUser/serializers.py

from django.forms import ValidationError
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import User

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from allauth.account.forms import ResetPasswordForm
from django.contrib.sites.shortcuts import get_current_site
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'profile_image')
        read_only_fields = ('id',)

class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password1 = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    profile_image = serializers.ImageField(required=False, allow_null=True)  # Champ optionnel
    username = serializers.CharField(required=False, allow_null=True)  # Champ optionnel

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'first_name', 'last_name', 'username', 'profile_image')

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cette adresse email est déjà utilisée.")
        return value

    def validate_username(self, value):
        if value and User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return value

    def validate_password1(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def create(self, validated_data):
        profile_image = validated_data.pop('profile_image', None)
        username = validated_data.pop('username', None)
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password1']
        )
        if profile_image:
            user.profile_image = profile_image
        if username:
            user.username = username
        user.save()
        return user



class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({
                "new_password2": "Les deux mots de passe ne correspondent pas."
            })
        return data



class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # Vérifie si l'email existe
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Aucun compte n'est associé à cette adresse email."
            )
        return value

    def save(self, request):
        try:
            # Utilise le formulaire de réinitialisation de mot de passe d'allauth
            form = ResetPasswordForm(data={'email': self.validated_data['email']})
            if form.is_valid():
                # Obtient le domaine du site actuel
                current_site = get_current_site(request)
                domain = current_site.domain
                
                # Envoie l'email de réinitialisation
                form.save(
                    request=request,
                    use_https=request.is_secure(),
                    domain=domain,
                )
                return True
            return False
        except Exception as e:
            raise serializers.ValidationError(str(e))


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)  # Email en lecture seule
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email','profile_image']
        
    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return value

    def update(self, instance, validated_data):
        # Mise à jour explicite des champs autorisés
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        instance.save()
        return instance
    
