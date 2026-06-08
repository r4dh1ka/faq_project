from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import CreateView

from community.models import UserBadge
from .forms import ProfileForm, RegisterForm
from .models import UserProfile


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'


class CustomLogoutView(LogoutView):
    next_page = 'faqs:home'
    http_method_names = ['get', 'post', 'options']

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


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
        user = form.save()
        
        # Send Verification Email
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verify_url = self.request.build_absolute_uri(
            reverse('accounts:verify_email', kwargs={'uidb64': uid, 'token': token})
        )
        
        subject = 'Verify your FAQ Platform account'
        html_content = render_to_string('accounts/verification_email_body.html', {
            'user': user,
            'verification_url': verify_url
        })
        msg = EmailMultiAlternatives(subject, "Please verify your email.", settings.DEFAULT_FROM_EMAIL, [user.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        return render(self.request, 'accounts/email_verification_sent.html', {'email': user.email})

class VerifyEmailView(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            profile = user.profile
            profile.is_email_verified = True
            profile.save()
            login(request, user)
            messages.success(request, 'Your email has been verified! Welcome to the community.')
            return redirect('faqs:home')
        else:
            messages.error(request, 'The verification link is invalid or has expired.')
            return redirect('accounts:login')


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
