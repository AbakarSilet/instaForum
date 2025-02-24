from celery import shared_task

from celery import shared_task
from django.utils import timezone
from .models import User

@shared_task
def check_suspended_users():
    suspended_users = User.objects.filter(is_suspended=True).exclude(suspension_date=None)
    for user in suspended_users:
        user.reactivate_if_suspension_expired()

@shared_task
def reactivate_user(user_id):
    from .models import User
    try:
        user = User.objects.get(id=user_id)
        user.reactivate_if_suspension_expired()
    except User.DoesNotExist:
        pass