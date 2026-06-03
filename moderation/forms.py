from django import forms

from .models import ContentReport, ReportReason


class ReportForm(forms.ModelForm):
    class Meta:
        model = ContentReport
        fields = ('reason', 'description')
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}
