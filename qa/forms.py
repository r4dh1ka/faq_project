from django import forms

from config.utils import sanitize_html
from .models import Answer, Question, Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
        widgets = {'body': forms.Textarea(attrs={'rows': 2, 'class': 'form-control mb-2', 'placeholder': 'Write a reply...'})}


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
