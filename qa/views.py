from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from community import services as community_services
from community.models import Notification
from faqs.search import find_similar_faqs, find_similar_questions
from faqs.models import ContentStatus
from .forms import AnswerForm, QuestionForm, CommentForm
from .models import (
    Answer, AnswerImage, AnswerVote, Question, QuestionBookmark, QuestionImage,
    QuestionVote, Comment, CommentVote,
)

MAX_IMAGES = 5


def _save_question_images(question, files):
    for idx, uploaded in enumerate(files[:MAX_IMAGES]):
        QuestionImage.objects.create(question=question, image=uploaded, order=idx)


def _save_answer_images(answer, files):
    for idx, uploaded in enumerate(files[:MAX_IMAGES]):
        AnswerImage.objects.create(answer=answer, image=uploaded, order=idx)


def question_list(request):
    sort = request.GET.get('sort', 'hot')
    q = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')
    tag = request.GET.get('tag', '').strip()

    questions = Question.objects.filter(status=ContentStatus.PUBLISHED).select_related(
        'author', 'category'
    ).prefetch_related('tags', 'images')

    if q:
        questions = questions.filter(
            Q(title__icontains=q) | Q(body__icontains=q) | Q(tags__name__icontains=q)
        ).distinct()
    if category_slug:
        questions = questions.filter(category__slug=category_slug)
    if tag:
        questions = questions.filter(tags__name__iexact=tag)

    if sort == 'top':
        questions = questions.order_by('-upvote_count', '-created_at')
    elif sort == 'views':
        questions = questions.order_by('-view_count', '-created_at')
    elif sort == 'unanswered':
        questions = questions.filter(is_answered=False).order_by('-created_at')
    else:
        questions = questions.order_by('-created_at')

    return render(request, 'qa/question_list.html', {
        'questions': questions[:100],
        'sort': sort,
        'search_query': q,
        'category_slug': category_slug,
        'tag': tag,
    })


def question_detail(request, pk):
    question = get_object_or_404(
        Question.objects.select_related('author', 'category').prefetch_related('tags', 'images'),
        pk=pk,
    )
    answers = question.answers.filter(status=ContentStatus.PUBLISHED).select_related(
        'author'
    ).prefetch_related('comments__author', 'comments__replies', 'images')
    similar_faqs = find_similar_faqs(question.title, limit=5)
    related_questions = find_similar_questions(question.title, exclude_pk=question.pk, limit=5)
    question.view_count += 1
    question.save(update_fields=['view_count'])
    form = AnswerForm() if request.user.is_authenticated else None
    comment_form = CommentForm() if request.user.is_authenticated else None
    bookmarked = False
    if request.user.is_authenticated:
        bookmarked = QuestionBookmark.objects.filter(user=request.user, question=question).exists()
    return render(request, 'qa/question_detail.html', {
        'question': question,
        'answers': answers,
        'similar_faqs': similar_faqs,
        'related_questions': related_questions,
        'form': form,
        'comment_form': comment_form,
        'bookmarked': bookmarked,
        'max_images': MAX_IMAGES,
    })


@login_required
def question_create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()
            form.save_m2m()
            images = request.FILES.getlist('images')
            if images:
                _save_question_images(question, images)

            from assistant.services import generate_ai_response
            from django.contrib.auth import get_user_model
            from config.utils import sanitize_html

            query = f"{question.title}\n{question.body}"
            ai_response = generate_ai_response(query)

            if ai_response and ai_response.get('reply') and "I couldn't find a matching FAQ" not in ai_response.get('reply'):
                User = get_user_model()
                bot_user, _ = User.objects.get_or_create(
                    username='YakshaBot',
                    defaults={'email': 'yakshabot@faqplatform.local', 'is_staff': True}
                )

                reply_text = sanitize_html(ai_response['reply'].replace('\n', '<br>'))
                if ai_response.get('sources'):
                    sources_html = "<br><br><hr><strong class='text-muted small'>Related Sources:</strong><ul class='small mb-0'>"
                    for src in ai_response['sources']:
                        sources_html += f"<li><a href='{src['url']}' class='text-decoration-none'>{src['title']}</a></li>"
                    sources_html += "</ul>"
                    reply_text += sanitize_html(sources_html)

                Answer.objects.create(
                    question=question,
                    author=bot_user,
                    body=reply_text,
                    status=ContentStatus.PUBLISHED,
                )

            messages.success(request, 'Question posted.')
            return redirect('qa:question_detail', pk=question.pk)
    else:
        form = QuestionForm()
    return render(request, 'qa/question_form.html', {'form': form, 'max_images': MAX_IMAGES})


@login_required
@require_POST
def question_vote(request, pk):
    question = get_object_or_404(Question, pk=pk)
    vote_type = int(request.POST.get('vote_type', 0))
    if vote_type not in (1, -1):
        return redirect('qa:question_detail', pk=question.pk)
    QuestionVote.objects.update_or_create(
        question=question, user=request.user, defaults={'vote_type': vote_type}
    )
    up = QuestionVote.objects.filter(question=question, vote_type=1).count()
    down = QuestionVote.objects.filter(question=question, vote_type=-1).count()
    Question.objects.filter(pk=question.pk).update(upvote_count=up, downvote_count=down)

    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('qa:question_detail', pk=question.pk)


@login_required
@require_POST
def toggle_question_bookmark(request, pk):
    question = get_object_or_404(Question, pk=pk)
    bookmark, created = QuestionBookmark.objects.get_or_create(user=request.user, question=question)
    if not created:
        bookmark.delete()
        messages.info(request, 'Question removed from bookmarks.')
    else:
        messages.success(request, 'Question saved to bookmarks.')
    return redirect('qa:question_detail', pk=pk)


@login_required
def question_bookmarks(request):
    items = QuestionBookmark.objects.filter(user=request.user).select_related(
        'question__author', 'question__category'
    ).prefetch_related('question__tags')
    return render(request, 'qa/bookmarks.html', {'bookmarks': items})


@login_required
@require_POST
def answer_create(request, pk):
    question = get_object_or_404(Question, pk=pk)
    form = AnswerForm(request.POST)
    if form.is_valid():
        answer = form.save(commit=False)
        answer.question = question
        answer.author = request.user
        answer.save()
        images = request.FILES.getlist('images')
        if images:
            _save_answer_images(answer, images)
        community_services.award_answer_points(answer)
        community_services.notify(
            question.author,
            Notification.NotificationType.ANSWER,
            f'{request.user.username} answered your question: {question.title}',
            question.get_absolute_url(),
        )
        messages.success(request, 'Answer posted.')
    return redirect('qa:question_detail', pk=pk)


@login_required
@require_POST
def answer_vote(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    vote_type = int(request.POST.get('vote_type', 0))
    if vote_type not in (1, -1):
        return redirect('qa:question_detail', pk=answer.question_id)
    AnswerVote.objects.update_or_create(
        answer=answer, user=request.user, defaults={'vote_type': vote_type}
    )
    up = AnswerVote.objects.filter(answer=answer, vote_type=1).count()
    down = AnswerVote.objects.filter(answer=answer, vote_type=-1).count()
    Answer.objects.filter(pk=answer.pk).update(upvote_count=up, downvote_count=down)
    if vote_type == 1:
        community_services.award_upvote_points(answer)
        community_services.notify(
            answer.author,
            Notification.NotificationType.UPVOTE,
            f'Your answer received an upvote on: {answer.question.title}',
            answer.question.get_absolute_url(),
        )
    return redirect('qa:question_detail', pk=answer.question_id)


@login_required
@require_POST
def comment_create(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    parent_id = request.POST.get('parent_id')
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.answer = answer
        if parent_id:
            try:
                parent = Comment.objects.get(pk=parent_id)
                if parent.answer_id == answer.pk:
                    comment.parent = parent
            except Comment.DoesNotExist:
                pass
        comment.save()
        messages.success(request, 'Your reply was posted.')
    return redirect('qa:question_detail', pk=answer.question.pk)


@login_required
@require_POST
def comment_vote(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    vote_type = int(request.POST.get('vote_type', 0))
    if vote_type not in (1, -1):
        return redirect('qa:question_detail', pk=comment.answer.question.pk)
    CommentVote.objects.update_or_create(
        comment=comment, user=request.user, defaults={'vote_type': vote_type}
    )
    up = CommentVote.objects.filter(comment=comment, vote_type=1).count()
    down = CommentVote.objects.filter(comment=comment, vote_type=-1).count()
    Comment.objects.filter(pk=comment.pk).update(upvote_count=up, downvote_count=down)

    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('qa:question_detail', pk=comment.answer.question.pk)


@login_required
@require_POST
def accept_answer(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    question = answer.question
    if question.author != request.user:
        messages.error(request, 'Only the question author can accept an answer.')
        return redirect('qa:question_detail', pk=question.pk)
    Answer.objects.filter(question=question).update(is_accepted=False)
    answer.is_accepted = True
    answer.save()
    question.is_answered = True
    question.save()
    community_services.award_accepted_points(answer)
    messages.success(request, 'Answer accepted.')
    return redirect('qa:question_detail', pk=question.pk)
