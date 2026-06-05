from django.urls import path

from . import views

app_name = 'qa'

urlpatterns = [
    path('', views.question_list, name='question_list'),
    path('ask/', views.question_create, name='question_create'),
    path('<int:pk>/', views.question_detail, name='question_detail'),
    path('<int:pk>/vote/', views.question_vote, name='question_vote'),
    path('<int:pk>/answer/', views.answer_create, name='answer_create'),
    path('answer/<int:pk>/vote/', views.answer_vote, name='answer_vote'),
    path('answer/<int:pk>/accept/', views.accept_answer, name='accept_answer'),
    path('answer/<int:pk>/comment/', views.comment_create, name='comment_create'),
    path('comment/<int:pk>/vote/', views.comment_vote, name='comment_vote'),
]
