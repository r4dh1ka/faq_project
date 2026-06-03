from collections import Counter

from django.db.models import Count
from django.shortcuts import render

from accounts.decorators import moderator_required
from faqs.models import FAQ, SearchLog, ContentStatus
from qa.models import Question, Answer


@moderator_required
def dashboard(request):
    most_viewed = FAQ.objects.filter(status=ContentStatus.PUBLISHED).order_by('-view_count')[:10]
    top_searches = (
        SearchLog.objects.values('query')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    unanswered = Question.objects.filter(is_answered=False).order_by('-created_at')[:10]
    trending_tags = Counter()
    for faq in FAQ.objects.filter(status=ContentStatus.PUBLISHED).prefetch_related('tags')[:100]:
        for tag in faq.tags.all():
            trending_tags[tag.name] += 1
    active_contributors = (
        Answer.objects.values('author__username')
        .annotate(answer_count=Count('id'))
        .order_by('-answer_count')[:10]
    )
    faq_growth = FAQ.objects.filter(status=ContentStatus.PUBLISHED).count()
    return render(request, 'analytics/dashboard.html', {
        'most_viewed': most_viewed,
        'top_searches': top_searches,
        'unanswered': unanswered,
        'trending_tags': trending_tags.most_common(10),
        'active_contributors': active_contributors,
        'faq_growth': faq_growth,
        'total_faqs': faq_growth,
        'total_questions': Question.objects.count(),
    })
