from django.urls import path

from . import views

app_name = 'qa'

urlpatterns = [
    path('', views.question_list, name='question_list'),
    path('ask/', views.question_create, name='question_create'),
    path('<int:pk>/', views.question_detail, name='question_detail'),
    path('<int:pk>/answer/', views.answer_create, name='answer_create'),
    path('answer/<int:pk>/vote/', views.answer_vote, name='answer_vote'),
    path('answer/<int:pk>/accept/', views.accept_answer, name='accept_answer'),
]
