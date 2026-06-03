from django.contrib import admin
from .models import Badge, Notification, ReputationLog, UserBadge


admin.site.register(Badge)
admin.site.register(UserBadge)
admin.site.register(ReputationLog)
admin.site.register(Notification)
