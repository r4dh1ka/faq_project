from django.contrib import admin
from .models import (
    Answer, AnswerImage, AnswerVote, Comment, CommentVote,
    Question, QuestionBookmark, QuestionImage, QuestionVote,
)


class QuestionImageInline(admin.TabularInline):
    model = QuestionImage
    extra = 0


class AnswerImageInline(admin.TabularInline):
    model = AnswerImage
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_answered', 'view_count', 'upvote_count')
    list_filter = ('is_answered', 'category', 'status')
    search_fields = ('title', 'body')
    inlines = [QuestionImageInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'author', 'is_accepted', 'upvote_count')
    inlines = [AnswerImageInline]


admin.site.register(QuestionImage)
admin.site.register(AnswerImage)
admin.site.register(QuestionBookmark)
admin.site.register(QuestionVote)
admin.site.register(AnswerVote)
admin.site.register(Comment)
admin.site.register(CommentVote)
