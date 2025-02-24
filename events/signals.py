#events/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.urls import reverse
from .models import Event
from modelUser.models import User
from forum.models import Notification
from django.utils.dateformat import format

@receiver(post_save, sender=Event)
def create_event_notification(sender, instance, created, **kwargs):
    if created:
        users = User.objects.all()
        event_url = reverse('event_detail', kwargs={'event_id': instance.id})
        for user in users:
            # Exclure le créateur de l'événement
            if user == instance.organizer:
                continue
            message = (
                f"{instance.organizer.first_name} {instance.organizer.last_name} a créé un nouvel événement '{instance.title}'\n\t"
                f"Lieu : {instance.location}\n\t"
                f"Le {format(instance.date, 'd M Y H:i')}\n\t"
                f"Participer en cliquant sur cette notifications"
            )
            Notification.objects.create(
                user=user,
                message=message,
                link=event_url  # Inclure le lien dans la notification
            )
