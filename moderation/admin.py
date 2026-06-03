from django.contrib import admin
from .models import ContentReport


@admin.register(ContentReport)
class ContentReportAdmin(admin.ModelAdmin):
    list_display = ('reason', 'reporter', 'is_resolved', 'created_at')
    list_filter = ('reason', 'is_resolved')
