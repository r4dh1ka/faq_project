from django.urls import path

from . import views

app_name = 'community'

urlpatterns = [
    path('leaderboard/', views.leaderboard, {'period': 'overall'}, name='leaderboard'),
    path('leaderboard/weekly/', views.leaderboard, {'period': 'weekly'}, name='leaderboard_weekly'),
    path('leaderboard/monthly/', views.leaderboard, {'period': 'monthly'}, name='leaderboard_monthly'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='notification_read'),
    path('notifications/read-all/', views.mark_all_read, name='notifications_read_all'),
]
