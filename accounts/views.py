from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView

from community.models import UserBadge
from .forms import ProfileForm, RegisterForm
from .models import UserProfile


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'


class CustomLogoutView(LogoutView):
    next_page = 'faqs:home'


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = '/accounts/login/'


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = '/'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Welcome! Your account has been created.')
        return response


@login_required
def profile_view(request, username=None):
    if username:
        profile = get_object_or_404(UserProfile, user__username=username)
    else:
        profile = request.user.profile
    badges = UserBadge.objects.filter(user=profile.user).select_related('badge')
    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'badges': badges,
        'is_own_profile': profile.user == request.user,
    })


@login_required
def profile_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/profile_edit.html', {'form': form})
