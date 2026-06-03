from django.urls import path

from . import views

app_name = 'assistant'

urlpatterns = [
    path('', views.chat_widget, name='widget'),
    path('api/chat/', views.chat_api, name='chat_api'),
]
