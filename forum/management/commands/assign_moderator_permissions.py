# management/commands/assign_moderator_permissions.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from forum.models import Thread, Post
from modelUser.models import User

class Command(BaseCommand):
    help = 'Assigne les permissions de modération au groupe Moderators'

    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name='Moderators')
        
        # Specifying the content types for the permissions
        thread_content_type = ContentType.objects.get_for_model(Thread)
        post_content_type = ContentType.objects.get_for_model(Post)

        # Getting permissions with specified content types
        thread_permission = Permission.objects.get(codename='delete_thread', content_type=thread_content_type)
        post_permission = Permission.objects.get(codename='delete_post', content_type=post_content_type)

        # Adding permissions to the group
        group.permissions.add(thread_permission, post_permission)
        
        # Adding custom suspend_user permission
        user_content_type = ContentType.objects.get_for_model(User)
        suspend_permission, created = Permission.objects.get_or_create(
            codename='suspend_user',
            name='Can suspend user',
            content_type=user_content_type,
        )
        group.permissions.add(suspend_permission)
        
        self.stdout.write(self.style.SUCCESS(f'Permissions de modération assignées au groupe Moderators'))
