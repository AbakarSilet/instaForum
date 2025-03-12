from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from django.core.cache import cache
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .utils import generate_profile_image
import os

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Le champ Email doit être renseigné')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superutilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superutilisateur doit avoir is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('adresse email'), unique=True)
    first_name = models.CharField(_('prénom'), max_length=150)
    last_name = models.CharField(_('nom'), max_length=150)
    profile_image = models.ImageField(_('image de profil'), upload_to='profiles_images/', blank=True, null=True)
    username = models.CharField(_('nom d\'utilisateur'), max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    suspension_date = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(_('date d\'inscription'), default=timezone.now) 


    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = f"{self.first_name.capitalize()}{self.last_name.capitalize()}"
            if User.objects.filter(username=self.username).exists():
                i = 1
                while User.objects.filter(username=f"{self.username}{i}").exists():
                    i += 1
                self.username = f"{self.username}{i}"

        if not self.profile_image:
            initials = f"{self.first_name[0].upper()}{self.last_name[0].upper()}"
            output_path = f'media/profiles_images/{self.username}_profile.png'
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            generate_profile_image(initials, output_path)
            self.profile_image.name = f'profiles_images/{self.username}_profile.png'

        super().save(*args, **kwargs)

    def suspend(self):
        self.is_suspended = True
        self.suspension_date = timezone.now()
        self.is_active = False
        self.save()
        
        # Programmer la réactivation
        from .tasks import reactivate_user
        reactivate_user.apply_async(args=[self.id], countdown=120)  # 120 secondes = 2 minutes

    def reactivate_if_suspension_expired(self):
        if self.is_suspended and self.suspension_date:
            suspension_duration = timezone.now() - self.suspension_date
            if suspension_duration.total_seconds() >= 120:  # 120 secondes = 2 minutes
                self.is_suspended = False
                self.is_active = True
                self.suspension_date = None
                self.save()

    def is_moderator(self):
        return self.groups.filter(name='Moderator').exists()

@receiver(post_save, sender=User)
def handle_user_suspension(sender, instance, **kwargs):
    if instance.is_suspended and instance.suspension_date:
        cache_key = f'user_suspension_{instance.id}'
        if not cache.get(cache_key):
            from .tasks import reactivate_user
            reactivate_user.apply_async(args=[instance.id], countdown=120)
            cache.set(cache_key, True, 120)
