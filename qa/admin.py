from django.contrib import admin
from .models import Answer, AnswerVote, Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_answered', 'view_count')
    search_fields = ('title', 'body')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'author', 'is_accepted', 'upvote_count')


admin.site.register(AnswerVote)
