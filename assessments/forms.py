from django import forms
from .models import Submission, Feedback

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['title', 'type', 'chapter', 'file', 'notes']
        widgets = {
            'type': forms.Select(choices=[
                ('draft', 'Draft'),
                ('final', 'Final'),
                ('proposal', 'Proposal'),
                ('revision', 'Revision'),
            ]),
            'chapter': forms.Select(choices=[
                ('1', 'Chapter 1'),
                ('2', 'Chapter 2'),
                ('3', 'Chapter 3'),
                ('4', 'Chapter 4'),
                ('5', 'Chapter 5'),
            ]),
            'notes': forms.Textarea(attrs={'placeholder': 'Describe changes made, key points, or anything the supervisor should note…'}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['submission', 'comment', 'score']
        widgets = {
            'comment': forms.Textarea(attrs={'placeholder': 'Provide your detailed feedback and comments here…'}),
            'score': forms.NumberInput(attrs={'min': 0, 'max': 100, 'placeholder': 'e.g. 85'}),
        }