from difflib import SequenceMatcher

from django.db.models import Q

from .models import FAQ, ContentStatus, SearchLog


def search_faqs(query='', category_slug='', tag='', sort='', user=None):
    qs = FAQ.objects.filter(status=ContentStatus.PUBLISHED).select_related('category', 'author').prefetch_related('tags')

    if category_slug:
        qs = qs.filter(category__slug=category_slug)
    if tag:
        qs = qs.filter(tags__name__iexact=tag)
    if query:
        qs = qs.filter(
            Q(title__icontains=query)
            | Q(question__icontains=query)
            | Q(answer__icontains=query)
            | Q(tags__name__icontains=query)
            | Q(category__name__icontains=query)
        ).distinct()

    if sort == 'popular':
        qs = qs.order_by('-upvote_count', '-view_count')
    elif sort == 'recent':
        qs = qs.order_by('-published_at', '-created_at')
    elif sort == 'views':
        qs = qs.order_by('-view_count')
    else:
        qs = qs.order_by('-upvote_count', '-view_count')

    results = list(qs[:50])
    if query:
        SearchLog.objects.create(query=query[:255], user=user, results_count=len(results))
    return results


def autocomplete_suggestions(prefix, limit=8):
    if not prefix or len(prefix) < 2:
        return []
    faqs = FAQ.objects.filter(
        status=ContentStatus.PUBLISHED,
        title__icontains=prefix,
    ).values_list('title', flat=True)[:limit]
    return list(faqs)


def find_similar_faqs(text, limit=5, threshold=0.55):
    published = FAQ.objects.filter(status=ContentStatus.PUBLISHED)[:200]
    scored = []
    text_lower = text.lower()
    for faq in published:
        ratio = SequenceMatcher(None, text_lower, faq.title.lower()).ratio()
        if ratio >= threshold:
            scored.append((ratio, faq))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [f for _, f in scored[:limit]]


def detect_duplicate_question(title, threshold=0.7):
  return find_similar_faqs(title, limit=3, threshold=threshold)
