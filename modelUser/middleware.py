#middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from .models import User

class ReactivateSuspendedUsersMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            user = request.user
            if user.is_suspended:
                user.reactivate_if_suspension_expired()
