from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .models import Role


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            profile = getattr(request.user, 'profile', None)
            if profile and profile.role in roles:
                return view_func(request, *args, **kwargs)
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('faqs:home')
        return _wrapped
    return decorator


moderator_required = role_required(Role.MODERATOR, Role.ADMIN)
admin_required = role_required(Role.ADMIN)
