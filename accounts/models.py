from django.conf import settings
from django.db import models


class Role(models.TextChoices):
    USER = 'user', 'User'
    MODERATOR = 'moderator', 'Moderator'
    ADMIN = 'admin', 'Administrator'


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    reputation = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-reputation']

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'

    @property
    def is_moderator(self):
        return self.role in (Role.MODERATOR, Role.ADMIN)

    @property
    def is_admin(self):
        return self.role == Role.ADMIN
