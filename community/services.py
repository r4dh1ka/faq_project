from django.conf import settings
from django.contrib.auth.models import User

from accounts.models import UserProfile
from .models import Badge, Notification, ReputationLog, UserBadge


def add_reputation(user: User, points: int, reason: str):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.reputation = max(0, profile.reputation + points)
    profile.save(update_fields=['reputation', 'updated_at'])
    ReputationLog.objects.create(user=user, points=points, reason=reason)
    _check_badges(user, profile.reputation)


def notify(user: User, notification_type: str, message: str, link: str = ''):
    Notification.objects.create(
        user=user,
        notification_type=notification_type,
        message=message,
        link=link,
    )


def _check_badges(user: User, reputation: int):
    badges = Badge.objects.filter(threshold__lte=reputation)
    for badge in badges:
        UserBadge.objects.get_or_create(user=user, badge=badge)

    if user.faqs.filter(status='published').exists():
        first, _ = Badge.objects.get_or_create(
            slug='first-contribution',
            defaults={'name': 'First Contribution', 'description': 'Posted your first FAQ', 'threshold': 0},
        )
        UserBadge.objects.get_or_create(user=user, badge=first)

    upvotes = sum(a.upvote_count for a in user.answers.all())
    if upvotes >= 100:
        badge, _ = Badge.objects.get_or_create(
            slug='100-upvotes',
            defaults={'name': '100 Upvotes', 'description': 'Received 100 upvotes on answers', 'threshold': 0},
        )
        UserBadge.objects.get_or_create(user=user, badge=badge)

    if reputation >= 500:
        badge, _ = Badge.objects.get_or_create(
            slug='top-contributor',
            defaults={'name': 'Top Contributor', 'description': 'Reached 500 reputation', 'threshold': 500},
        )
        UserBadge.objects.get_or_create(user=user, badge=badge)


def award_answer_points(answer):
    add_reputation(answer.author, settings.POINTS_ANSWER_POSTED, 'Answer posted')


def award_upvote_points(answer):
    add_reputation(answer.author, settings.POINTS_UPVOTE_RECEIVED, 'Answer upvoted')


def award_accepted_points(answer):
    add_reputation(answer.author, settings.POINTS_ACCEPTED_ANSWER, 'Accepted answer')


def award_faq_points(user):
    add_reputation(user, settings.POINTS_FAQ_CONTRIBUTION, 'FAQ published')


def award_edit_points(user):
    add_reputation(user, settings.POINTS_EDIT_ACCEPTED, 'Edit suggestion accepted')
