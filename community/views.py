from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import UserProfile
from .models import Notification, ReputationLog


def leaderboard(request, period='overall'):
    users = UserProfile.objects.select_related('user').order_by('-reputation')
    if period == 'weekly':
        since = timezone.now() - timedelta(days=7)
        scores = (
            ReputationLog.objects.filter(created_at__gte=since)
            .values('user')
            .annotate(period_points=Sum('points'))
            .order_by('-period_points')[:20]
        )
        user_ids = [s['user'] for s in scores]
        users = UserProfile.objects.filter(user_id__in=user_ids).select_related('user')
        score_map = {s['user']: s['period_points'] for s in scores}
        ranked = sorted(users, key=lambda p: score_map.get(p.user_id, 0), reverse=True)
        for p in ranked:
            p.display_points = score_map.get(p.user_id, 0)
        return render(request, 'community/leaderboard.html', {
            'profiles': ranked,
            'period': period,
            'use_period_points': True,
        })
    if period == 'monthly':
        since = timezone.now() - timedelta(days=30)
        scores = (
            ReputationLog.objects.filter(created_at__gte=since)
            .values('user')
            .annotate(period_points=Sum('points'))
            .order_by('-period_points')[:20]
        )
        user_ids = [s['user'] for s in scores]
        users = UserProfile.objects.filter(user_id__in=user_ids).select_related('user')
        score_map = {s['user']: s['period_points'] for s in scores}
        ranked = sorted(users, key=lambda p: score_map.get(p.user_id, 0), reverse=True)
        for p in ranked:
            p.display_points = score_map.get(p.user_id, 0)
        return render(request, 'community/leaderboard.html', {
            'profiles': ranked,
            'period': period,
            'use_period_points': True,
        })
    profiles = list(users[:20])
    for p in profiles:
        p.display_points = p.reputation
    return render(request, 'community/leaderboard.html', {
        'profiles': profiles,
        'period': period,
        'use_period_points': False,
    })


@login_required
def notifications(request):
    items = request.user.notifications.all()[:50]
    return render(request, 'community/notifications.html', {'notifications': items})


@login_required
@require_POST
def mark_notification_read(request, pk):
    note = get_object_or_404(Notification, pk=pk, user=request.user)
    note.is_read = True
    note.save()
    if note.link:
        return redirect(note.link)
    return redirect('community:notifications')


@login_required
@require_POST
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('community:notifications')
