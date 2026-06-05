from django.contrib import admin
from .models import Bookmark, Category, FAQ, FAQEditSuggestion, FAQVote, SearchLog, Subcategory


class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 0
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SubcategoryInline]
    list_display = ('name', 'slug', 'icon')


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'order')
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'subcategory', 'status', 'author', 'view_count', 'upvote_count')
    list_filter = ('status', 'category', 'subcategory')
    search_fields = ('title', 'question', 'answer')
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(FAQEditSuggestion)
admin.site.register(FAQVote)
admin.site.register(Bookmark)
admin.site.register(SearchLog)
