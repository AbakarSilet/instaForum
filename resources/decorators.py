from django.core.exceptions import PermissionDenied
from functools import wraps

def teacher_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.groups.filter(name='Teacher').exists():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def moderator_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.groups.filter(name='Moderator').exists():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view