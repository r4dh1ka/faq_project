from django import forms

from config.utils import sanitize_html
from .models import Answer, Question


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('title', 'body', 'category', 'tags')
        widgets = {
            'title': forms.TextInput(attrs={'id': 'question-title'}),
            'body': forms.Textarea(attrs={'rows': 6, 'class': 'rich-text'}),
        }

    def clean_body(self):
        return sanitize_html(self.cleaned_data.get('body', ''))


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('body',)
        widgets = {'body': forms.Textarea(attrs={'rows': 6, 'class': 'rich-text'})}

    def clean_body(self):
        return sanitize_html(self.cleaned_data.get('body', ''))
