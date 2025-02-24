# messaging/models.py
from django.db import models
from django.db.models import Q
from django.conf import settings
from django.forms import ValidationError
from django.utils import timezone
from django.core.validators import URLValidator


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    def save(self, *args, **kwargs):
        # Vérifier le blocage avant d'enregistrer le message
        if not self.pk:  # Nouveau message uniquement
            is_blocked = UserBlock.objects.filter(
                Q(blocker=self.receiver, blocked=self.sender)
            ).exists()
            
            if is_blocked:
                raise ValidationError("Vous ne pouvez pas envoyer de message à cet utilisateur car il vous a bloqué.")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.created_at}"

class SharedLink(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='shared_links')
    url = models.URLField(validators=[URLValidator()])
    link_type = models.CharField(max_length=10, choices=[('DRIVE', 'Google Drive'), ('YOUTUBE', 'YouTube'), ('OTHER', 'Other')])
    title = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.url

class UserBlock(models.Model):
    blocker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blocking')
    blocked = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blocked_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['blocker', 'blocked']

    def save(self, *args, **kwargs):
        if self.blocker == self.blocked:
            raise ValidationError("Vous ne pouvez pas vous bloquer vous-même.")
        super().save(*args, **kwargs)
