from django import forms
from .models import Submission, Feedback

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['title', 'type', 'chapter', 'file', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Chapter 4: Data Analysis — Revised'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'chapter': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-input', 'style': 'padding:0.55rem 0.9rem'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Describe changes made, key points, or anything the supervisor should note…'}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['submission', 'comment', 'score']
        widgets = {
            'comment': forms.Textarea(attrs={'placeholder': 'Provide your detailed feedback and comments here…'}),
            'score': forms.NumberInput(attrs={'min': 0, 'max': 100, 'placeholder': 'e.g. 85'}),
        }