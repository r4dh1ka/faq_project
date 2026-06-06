from django.urls import path

from . import views

app_name = 'faqs'

urlpatterns = [
    path('', views.home, name='home'),
    path('browse/', views.faq_list, name='list'),
    path('submit/', views.faq_create, name='create'),
    path('my-submissions/', views.my_submissions, name='my_submissions'),
    path('bookmarks/', views.bookmarks, name='bookmarks'),
    path('category/<slug:slug>/', views.category_view, name='category'),
    path('category/<slug:category_slug>/<slug:slug>/', views.subcategory_view, name='subcategory'),
    path('faq/<slug:slug>/', views.faq_detail, name='detail'),
    path('faq/<slug:slug>/edit-suggest/', views.faq_edit_suggest, name='edit_suggest'),
    path('faq/<slug:slug>/vote/', views.faq_vote, name='vote'),
    path('faq/<slug:slug>/bookmark/', views.toggle_bookmark, name='bookmark'),
    path('search/autocomplete/', views.search_autocomplete, name='autocomplete'),
    path('search/duplicate-check/', views.duplicate_check, name='duplicate_check'),
    path('moderation/pending/', views.pending_faqs, name='pending'),
    path('moderation/approve/<int:pk>/', views.approve_faq, name='approve'),
    path('moderation/reject/<int:pk>/', views.reject_faq, name='reject'),
    path('moderation/edit/<int:pk>/approve/', views.approve_edit, name='approve_edit'),
]
