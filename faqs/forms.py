from django import forms

from config.utils import sanitize_html
from .models import FAQ, FAQEditSuggestion, ContentStatus


class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ('title', 'question', 'answer', 'category', 'tags', 'attachment', 'image')
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3}),
            'answer': forms.Textarea(attrs={'rows': 8, 'class': 'rich-text'}),
        }

    def clean_answer(self):
        return sanitize_html(self.cleaned_data.get('answer', ''))

    def clean_question(self):
        return sanitize_html(self.cleaned_data.get('question', ''))


class FAQEditSuggestionForm(forms.ModelForm):
    class Meta:
        model = FAQEditSuggestion
        fields = ('title', 'question', 'answer')
        widgets = {'answer': forms.Textarea(attrs={'rows': 8})}

    def clean_answer(self):
        return sanitize_html(self.cleaned_data.get('answer', ''))


class FAQSearchForm(forms.Form):
    q = forms.CharField(required=False, label='Search')
    category = forms.CharField(required=False)
    tag = forms.CharField(required=False)
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Relevance'),
            ('popular', 'Most Popular'),
            ('recent', 'Most Recent'),
            ('views', 'Most Viewed'),
        ],
    )
