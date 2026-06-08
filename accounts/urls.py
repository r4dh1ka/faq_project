from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('user/<str:username>/', views.profile_view, name='user_profile'),
    path('verify-email/<str:uidb64>/<str:token>/', views.VerifyEmailView.as_view(), name='verify_email'),
]
