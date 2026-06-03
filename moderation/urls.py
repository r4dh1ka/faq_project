from django.urls import path

from . import views

app_name = 'moderation'

urlpatterns = [
    path('report/<str:app_label>/<str:model>/<int:object_id>/', views.report_content, name='report'),
    path('reports/', views.report_list, name='report_list'),
    path('reports/<int:pk>/resolve/', views.resolve_report, name='resolve_report'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
