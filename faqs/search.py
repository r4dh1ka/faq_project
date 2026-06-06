from difflib import SequenceMatcher

from django.db.models import Q

from .models import FAQ, ContentStatus, SearchLog


def search_faqs(query='', category_slug='', tag='', sort='', user=None, subcategory_slug=''):
    qs = FAQ.objects.filter(status=ContentStatus.PUBLISHED).select_related(
        'category', 'subcategory', 'author'
    ).prefetch_related('tags')

    if category_slug:
        qs = qs.filter(category__slug=category_slug)
    if subcategory_slug:
        qs = qs.filter(subcategory__slug=subcategory_slug)
    if tag:
        qs = qs.filter(tags__name__iexact=tag)
    if query:
        qs = qs.filter(
            Q(title__icontains=query)
            | Q(question__icontains=query)
            | Q(answer__icontains=query)
            | Q(tags__name__icontains=query)
            | Q(category__name__icontains=query)
            | Q(subcategory__name__icontains=query)
        ).distinct()

    if sort == 'popular':
        qs = qs.order_by('-upvote_count', '-view_count')
    elif sort == 'recent':
        qs = qs.order_by('-published_at', '-created_at')
    elif sort == 'views':
        qs = qs.order_by('-view_count')
    elif sort == 'title':
        qs = qs.order_by('title')
    else:
        qs = qs.order_by('-upvote_count', '-view_count')

    results = list(qs[:100])
    if query:
        SearchLog.objects.create(query=query[:255], user=user, results_count=len(results))
    return results


def search_questions(query='', category_slug='', tag='', sort=''):
    from qa.models import Question
    from faqs.models import ContentStatus as CS

    qs = Question.objects.filter(status=CS.PUBLISHED).select_related('author', 'category').prefetch_related('tags')
    if category_slug:
        qs = qs.filter(category__slug=category_slug)
    if tag:
        qs = qs.filter(tags__name__iexact=tag)
    if query:
        qs = qs.filter(
            Q(title__icontains=query)
            | Q(body__icontains=query)
            | Q(tags__name__icontains=query)
            | Q(answers__body__icontains=query)
        ).distinct()
    if sort == 'popular':
        qs = qs.order_by('-upvote_count', '-view_count')
    elif sort == 'views':
        qs = qs.order_by('-view_count')
    elif sort == 'unanswered':
        qs = qs.filter(is_answered=False).order_by('-created_at')
    else:
        qs = qs.order_by('-created_at')
    return list(qs[:50])


def unified_search(query, category_slug='', tag='', sort='', user=None):
    """Full-text style search across FAQs and community questions."""
    faqs = search_faqs(query, category_slug, tag, sort, user) if query or category_slug or tag else []
    questions = search_questions(query, category_slug, tag, sort) if query else []
    return faqs, questions


def autocomplete_suggestions(prefix, limit=10):
    if not prefix or len(prefix) < 2:
        return []
    faq_titles = FAQ.objects.filter(
        status=ContentStatus.PUBLISHED,
        title__icontains=prefix,
    ).values_list('title', flat=True)[:limit]
    from qa.models import Question
    q_titles = Question.objects.filter(
        status=ContentStatus.PUBLISHED,
        title__icontains=prefix,
    ).values_list('title', flat=True)[:limit]
    combined = list(dict.fromkeys(list(faq_titles) + list(q_titles)))
    return combined[:limit]


def find_similar_faqs(text, limit=5, threshold=0.55):
    published = FAQ.objects.filter(status=ContentStatus.PUBLISHED).select_related('category')[:300]
    scored = []
    text_lower = text.lower()
    for faq in published:
        ratio = SequenceMatcher(None, text_lower, faq.title.lower()).ratio()
        if ratio >= threshold:
            scored.append((ratio, faq))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [f for _, f in scored[:limit]]


def find_similar_questions(text, limit=5, threshold=0.5, exclude_pk=None):
    from qa.models import Question
    from faqs.models import ContentStatus as CS

    qs = Question.objects.filter(status=CS.PUBLISHED).select_related('author', 'category')
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    scored = []
    text_lower = text.lower()
    for question in qs[:200]:
        ratio = SequenceMatcher(None, text_lower, question.title.lower()).ratio()
        if ratio >= threshold:
            scored.append((ratio, question))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [q for _, q in scored[:limit]]


def detect_duplicate_question(title, threshold=0.7):
    faqs = find_similar_faqs(title, limit=3, threshold=threshold)
    questions = find_similar_questions(title, limit=3, threshold=threshold)
    combined = faqs + questions
    return combined[:3]
