from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from .models import Thread, Post, Like, Badge, UserBadge
from django.utils.dateformat import format

@receiver(post_save, sender=Thread)
def award_thread_badge(sender, instance, created, **kwargs):
    if created:
        user = instance.author
        if Thread.objects.filter(author=user).count() >= 10:  # nbre des threads pour dire actif
            badge = Badge.objects.get(name="Auteur Actif")
            if not UserBadge.objects.filter(user=user, badge=badge).exists():
                UserBadge.objects.create(user=user, badge=badge)
            # Notification.objects.create(
            #     user=user,
            #     message=f'Félicitations {instance.author.username}, vous gagnez le badge d\'auteur actif. Merci pour votre contribution à la communauté',
            #     link=reverse('forum:profile', kwargs={'username':instance.author.username} )
            # )

@receiver(post_save, sender=Like)
def award_like_badge(sender, instance, created, **kwargs):
    if created:
        user = instance.thread.author
        if Like.objects.filter(thread__author=user).count() >= 100:  
            badge = Badge.objects.get(name="Populaire")
            if not UserBadge.objects.filter(user=user, badge=badge).exists():
                UserBadge.objects.create(user=user, badge=badge)
                
@receiver(post_save, sender=Post)
def award_comment_badge(sender, instance, created, **kwargs):
    if created:
        user = instance.author
        if Post.objects.filter(author=user).count() >= 50:
            badge = Badge.objects.get(name="Commentateur Actif")
            if not UserBadge.objects.filter(user=user, badge=badge).exists():
                UserBadge.objects.create(user=user, badge=badge)

@receiver(post_save, sender=Post)
def create_post_notification(sender, instance, created, **kwargs):
    if created:
        thread_author = instance.thread.author
        if instance.author != thread_author:
            thread_url = reverse('forum:thread', kwargs={'slug': instance.thread.slug})
            




