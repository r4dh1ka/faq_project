from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import admin_required, moderator_required
from .forms import ReportForm
from .models import ContentReport


@login_required
def report_content(request, app_label, model, object_id):
    ct = get_object_or_404(ContentType, app_label=app_label, model=model)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.content_type = ct
            report.object_id = object_id
            report.save()
            messages.success(request, 'Report submitted. Moderators will review it.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        form = ReportForm()
    return render(request, 'moderation/report.html', {'form': form})


@moderator_required
def report_list(request):
    reports = ContentReport.objects.filter(is_resolved=False).select_related('reporter', 'content_type')
    return render(request, 'moderation/report_list.html', {'reports': reports})


@moderator_required
@require_POST
def resolve_report(request, pk):
    report = get_object_or_404(ContentReport, pk=pk)
    report.is_resolved = True
    report.resolved_by = request.user
    report.resolution_note = request.POST.get('note', '')
    report.save()
    messages.success(request, 'Report resolved.')
    return redirect('moderation:report_list')


@admin_required
def admin_dashboard(request):
    from django.contrib.auth.models import User
    from faqs.models import FAQ, ContentStatus
    from qa.models import Question

    stats = {
        'users': User.objects.count(),
        'faqs_published': FAQ.objects.filter(status=ContentStatus.PUBLISHED).count(),
        'faqs_pending': FAQ.objects.filter(status=ContentStatus.PENDING).count(),
        'questions': Question.objects.count(),
        'open_reports': ContentReport.objects.filter(is_resolved=False).count(),
    }
    return render(request, 'moderation/admin_dashboard.html', {'stats': stats})
