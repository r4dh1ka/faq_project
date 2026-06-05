from django.conf import settings
from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager

from faqs.models import ContentStatus


class Question(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='questions')
    category = models.ForeignKey('faqs.Category', on_delete=models.SET_NULL, null=True, blank=True)
    tags = TaggableManager(blank=True)
    view_count = models.PositiveIntegerField(default=0)
    is_answered = models.BooleanField(default=False)
    upvote_count = models.PositiveIntegerField(default=0)
    downvote_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=ContentStatus.choices, default=ContentStatus.PUBLISHED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('qa:question_detail', kwargs={'pk': self.pk})

    @property
    def answer_count(self):
        return self.answers.filter(status=ContentStatus.PUBLISHED).count()

    @property
    def score(self):
        return self.upvote_count - self.downvote_count


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='answers')
    body = models.TextField()
    is_accepted = models.BooleanField(default=False)
    upvote_count = models.PositiveIntegerField(default=0)
    downvote_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=ContentStatus.choices, default=ContentStatus.PUBLISHED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_accepted', '-upvote_count', 'created_at']

    def __str__(self):
        return f'Answer by {self.author.username} on {self.question.title}'

    @property
    def score(self):
        return self.upvote_count - self.downvote_count


class QuestionVote(models.Model):
    class VoteType(models.IntegerChoices):
        UP = 1, 'Upvote'
        DOWN = -1, 'Downvote'

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vote_type = models.SmallIntegerField(choices=VoteType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('question', 'user')

    def __str__(self):
        return f'{self.user.username} voted {self.get_vote_type_display()} on {self.question.title}'


class AnswerVote(models.Model):
    class VoteType(models.IntegerChoices):
        UP = 1, 'Upvote'
        DOWN = -1, 'Downvote'

    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vote_type = models.SmallIntegerField(choices=VoteType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('answer', 'user')


class Comment(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    upvote_count = models.PositiveIntegerField(default=0)
    downvote_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username}'

    @property
    def score(self):
        return self.upvote_count - self.downvote_count


class CommentVote(models.Model):
    class VoteType(models.IntegerChoices):
        UP = 1, 'Upvote'
        DOWN = -1, 'Downvote'

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vote_type = models.SmallIntegerField(choices=VoteType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'user')
