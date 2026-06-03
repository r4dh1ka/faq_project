from django.contrib import admin
from .models import Bookmark, Category, FAQ, FAQEditSuggestion, FAQVote, SearchLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'author', 'view_count', 'upvote_count')
    list_filter = ('status', 'category')
    search_fields = ('title', 'question', 'answer')
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(FAQEditSuggestion)
admin.site.register(FAQVote)
admin.site.register(Bookmark)
admin.site.register(SearchLog)
