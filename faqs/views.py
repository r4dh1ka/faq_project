from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from accounts.decorators import moderator_required
from community import services as community_services
from community.models import Notification
from .forms import FAQEditSuggestionForm, FAQForm, FAQSearchForm
from .models import Bookmark, Category, ContentStatus, FAQ, FAQEditSuggestion, FAQVote
from qa.models import Question

from .search import (
    autocomplete_suggestions,
    detect_duplicate_question,
    find_similar_faqs,
    find_similar_questions,
    search_faqs,
    search_questions,
    unified_search,
)


def home(request):
    published = FAQ.objects.filter(status=ContentStatus.PUBLISHED)
    trending = published.select_related('category', 'author').prefetch_related('tags').order_by(
        '-view_count', '-upvote_count'
    )[:6]
    featured = published.filter(upvote_count__gte=10).order_by('-upvote_count', '-view_count')[:6]
    if featured.count() < 4:
        featured = trending
    recent_faqs = published.select_related('category', 'author').prefetch_related('tags').order_by(
        '-published_at', '-created_at'
    )[:6]
    categories = Category.objects.prefetch_related('subcategories').all()
    recent_questions = Question.objects.filter(status=ContentStatus.PUBLISHED).select_related(
        'author', 'category'
    ).order_by('-created_at')[:6]
    most_viewed_questions = Question.objects.filter(status=ContentStatus.PUBLISHED).order_by(
        '-view_count'
    )[:5]
    unanswered = Question.objects.filter(status=ContentStatus.PUBLISHED, is_answered=False).order_by(
        '-created_at'
    )[:5]
    return render(request, 'faqs/home.html', {
        'trending': trending,
        'featured': featured,
        'recent_faqs': recent_faqs,
        'categories': categories,
        'recent_questions': recent_questions,
        'most_viewed_questions': most_viewed_questions,
        'unanswered': unanswered,
        'faq_total': published.count(),
    })


def faq_list(request):
    form = FAQSearchForm(request.GET or None)
    query = category = tag = sort = ''
    if form.is_valid():
        query = form.cleaned_data.get('q', '')
        category = form.cleaned_data.get('category', '')
        tag = form.cleaned_data.get('tag', '')
        sort = form.cleaned_data.get('sort', '')
    user = request.user if request.user.is_authenticated else None
    if query:
        faqs, community_questions = unified_search(query, category, tag, sort, user)
    else:
        faqs = search_faqs(query, category, tag, sort, user)
        community_questions = search_questions(query, category, tag, sort) if category or tag else []
    return render(request, 'faqs/list.html', {
        'faqs': faqs,
        'community_questions': community_questions,
        'form': form,
        'search_query': query,
    })


def faq_detail(request, slug):
    faq = get_object_or_404(
        FAQ.objects.select_related('category', 'subcategory', 'author').prefetch_related('tags'),
        slug=slug,
        status=ContentStatus.PUBLISHED,
    )
    FAQ.objects.filter(pk=faq.pk).update(view_count=F('view_count') + 1)
    faq.refresh_from_db()
    related = find_similar_faqs(faq.title, limit=6)
    related_questions = find_similar_questions(faq.title, limit=4)
    bookmarked = False
    if request.user.is_authenticated:
        bookmarked = Bookmark.objects.filter(user=request.user, faq=faq).exists()
    return render(request, 'faqs/detail.html', {
        'faq': faq,
        'related': [r for r in related if r.pk != faq.pk],
        'related_questions': related_questions,
        'bookmarked': bookmarked,
    })


def category_view(request, slug):
    category = get_object_or_404(Category.objects.prefetch_related('subcategories'), slug=slug)
    faqs = FAQ.objects.filter(category=category, status=ContentStatus.PUBLISHED).select_related(
        'author', 'subcategory'
    ).prefetch_related('tags').order_by('subcategory__order', 'subcategory__name', 'title')
    subcategory_groups = {}
    for faq in faqs:
        key = faq.subcategory.name if faq.subcategory else 'General'
        subcategory_groups.setdefault(key, []).append(faq)
    return render(request, 'faqs/category.html', {
        'category': category,
        'faqs': faqs,
        'subcategory_groups': subcategory_groups,
    })


def subcategory_view(request, category_slug, slug):
    category = get_object_or_404(Category, slug=category_slug)
    subcategory = get_object_or_404(category.subcategories, slug=slug)
    faqs = FAQ.objects.filter(
        category=category, subcategory=subcategory, status=ContentStatus.PUBLISHED
    ).select_related('author').prefetch_related('tags')
    return render(request, 'faqs/subcategory.html', {
        'category': category,
        'subcategory': subcategory,
        'faqs': faqs,
    })


@login_required
def faq_create(request):
    if request.method == 'POST':
        form = FAQForm(request.POST, request.FILES)
        if form.is_valid():
            faq = form.save(commit=False)
            faq.author = request.user
            faq.status = ContentStatus.PENDING
            faq.save()
            form.save_m2m()
            messages.success(request, 'FAQ submitted for moderator review.')
            return redirect('faqs:my_submissions')
    else:
        form = FAQForm()
    return render(request, 'faqs/form.html', {'form': form, 'title': 'Submit FAQ'})


@login_required
def faq_edit_suggest(request, slug):
    faq = get_object_or_404(FAQ, slug=slug, status=ContentStatus.PUBLISHED)
    if request.method == 'POST':
        form = FAQEditSuggestionForm(request.POST)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.faq = faq
            suggestion.suggested_by = request.user
            suggestion.save()
            messages.success(request, 'Edit suggestion submitted for review.')
            return redirect('faqs:detail', slug=slug)
    else:
        form = FAQEditSuggestionForm(initial={
            'title': faq.title,
            'question': faq.question,
            'answer': faq.answer,
        })
    return render(request, 'faqs/edit_suggest.html', {'form': form, 'faq': faq})


@login_required
def my_submissions(request):
    faqs = FAQ.objects.filter(author=request.user).select_related('category').prefetch_related('tags')
    return render(request, 'faqs/my_submissions.html', {'faqs': faqs})


@login_required
@require_POST
def faq_vote(request, slug):
    faq = get_object_or_404(FAQ, slug=slug, status=ContentStatus.PUBLISHED)
    vote_type = int(request.POST.get('vote_type', 0))
    if vote_type not in (1, -1):
        messages.error(request, 'Invalid vote.')
        return redirect('faqs:detail', slug=slug)
    vote, created = FAQVote.objects.update_or_create(
        faq=faq, user=request.user, defaults={'vote_type': vote_type}
    )
    up = FAQVote.objects.filter(faq=faq, vote_type=1).count()
    down = FAQVote.objects.filter(faq=faq, vote_type=-1).count()
    FAQ.objects.filter(pk=faq.pk).update(upvote_count=up, downvote_count=down)
    return redirect('faqs:detail', slug=slug)


@login_required
@require_POST
def toggle_bookmark(request, slug):
    faq = get_object_or_404(FAQ, slug=slug)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, faq=faq)
    if not created:
        bookmark.delete()
        messages.info(request, 'Removed from bookmarks.')
    else:
        messages.success(request, 'Saved to bookmarks.')
    return redirect('faqs:detail', slug=slug)


@login_required
def bookmarks(request):
    items = Bookmark.objects.filter(user=request.user).select_related('faq__category', 'faq__author').prefetch_related('faq__tags')
    return render(request, 'faqs/bookmarks.html', {'bookmarks': items})


@require_GET
def search_autocomplete(request):
    q = request.GET.get('q', '')
    return JsonResponse({'suggestions': autocomplete_suggestions(q)})


@require_GET
def duplicate_check(request):
    title = request.GET.get('title', '')
    similar = detect_duplicate_question(title)
    return JsonResponse({
        'duplicates': [{'title': f.title, 'url': f.get_absolute_url()} for f in similar],
    })


@moderator_required
def pending_faqs(request):
    pending = FAQ.objects.filter(status=ContentStatus.PENDING).select_related('category', 'author').prefetch_related('tags')
    edits = FAQEditSuggestion.objects.filter(status=ContentStatus.PENDING).select_related('faq', 'suggested_by')
    return render(request, 'faqs/pending.html', {'pending': pending, 'edits': edits})


@moderator_required
@require_POST
def approve_faq(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    faq.status = ContentStatus.PUBLISHED
    faq.published_at = timezone.now()
    faq.version += 1
    faq.save()
    if faq.author:
        community_services.award_faq_points(faq.author)
        community_services.notify(
            faq.author,
            Notification.NotificationType.FAQ_APPROVED,
            f'Your FAQ "{faq.title}" has been approved.',
            faq.get_absolute_url(),
        )
    messages.success(request, f'FAQ "{faq.title}" published.')
    return redirect('faqs:pending')


@moderator_required
@require_POST
def reject_faq(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    faq.status = ContentStatus.REJECTED
    faq.save()
    messages.warning(request, f'FAQ "{faq.title}" rejected.')
    return redirect('faqs:pending')


@moderator_required
@require_POST
def approve_edit(request, pk):
    suggestion = get_object_or_404(FAQEditSuggestion, pk=pk)
    faq = suggestion.faq
    if suggestion.title:
        faq.title = suggestion.title
    if suggestion.question:
        faq.question = suggestion.question
    faq.answer = suggestion.answer
    faq.version += 1
    faq.save()
    suggestion.status = ContentStatus.PUBLISHED
    suggestion.save()
    community_services.award_edit_points(suggestion.suggested_by)
    messages.success(request, 'Edit applied.')
    return redirect('faqs:pending')
