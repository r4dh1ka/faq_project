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
    is_email_verified = models.BooleanField(default=False)
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

    @property
    def badge(self):
        if self.reputation >= 500:
            return {'name': 'Diamond Guru', 'icon': 'bi-gem', 'color': 'text-info'}
        elif self.reputation >= 300:
            return {'name': 'Platinum Guide', 'icon': 'bi-star-fill', 'color': 'text-primary'}
        elif self.reputation >= 150:
            return {'name': 'Gold Contributor', 'icon': 'bi-award-fill', 'color': 'text-warning'}
        elif self.reputation >= 50:
            return {'name': 'Silver Helper', 'icon': 'bi-shield-fill-check', 'color': 'text-secondary'}
        return None
