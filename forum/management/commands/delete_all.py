from django.core.management.base import BaseCommand
from forum.models import Dislike, Like, Thread, Subforum, Post,Notification, Report

class Command(BaseCommand):
    help = 'Delete all data from forum application'

    def handle(self, *args, **kwargs):
        Thread.objects.all().delete()
        Subforum.objects.all().delete()
        Post.objects.all().delete()
        Report.objects.all().delete()
        Notification.objects.all().delete()
        Like.objects.all().delete()
        Dislike.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all data from forum application'))
