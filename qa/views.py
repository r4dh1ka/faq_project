from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from community import services as community_services
from community.models import Notification
from faqs.search import find_similar_faqs
from .forms import AnswerForm, QuestionForm
from .models import Answer, AnswerVote, Question


def question_list(request):
    questions = Question.objects.select_related('author', 'category').prefetch_related('tags')
    return render(request, 'qa/question_list.html', {'questions': questions})


def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    Question.objects.filter(pk=question.pk).update(view_count=F('view_count') + 1)
    answers = question.answers.select_related('author')
    form = AnswerForm() if request.user.is_authenticated else None
    similar_faqs = find_similar_faqs(question.title, limit=4)
    return render(request, 'qa/question_detail.html', {
        'question': question,
        'answers': answers,
        'form': form,
        'similar_faqs': similar_faqs,
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
            messages.success(request, 'Question posted.')
            return redirect('qa:question_detail', pk=question.pk)
    else:
        form = QuestionForm()
    return render(request, 'qa/question_form.html', {'form': form})


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
