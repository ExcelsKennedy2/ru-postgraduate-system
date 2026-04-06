from django import forms
from .models import PresentationBooking, QuarterlyReport, Student

class PresentationBookingForm(forms.ModelForm):
    class Meta:
        model = PresentationBooking
        fields = ['title', 'date', 'meeting_type', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Chapter 4 revision discussion'
            }),
            'date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-input'
            }),
            'meeting_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Any specific topics or documents to review…'
            }),
        }

class StudentProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        label='First Name',
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    last_name = forms.CharField(
        label='Last Name',
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = Student
        fields = ['student_number', 'programme']
        widgets = {
            'student_number': forms.TextInput(attrs={
                'class': 'form-input',
                'readonly': 'readonly'
            }),
            'programme': forms.TextInput(attrs={
                'class': 'form-input',
                'readonly': 'readonly'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        student = super().save(commit=False)
        user = student.user
        user.first_name = self.cleaned_data.get('first_name', user.first_name)
        user.last_name = self.cleaned_data.get('last_name', user.last_name)
        user.email = self.cleaned_data.get('email', user.email)
        if commit:
            user.save()
            student.save()
        return student

class QuarterlyReportForm(forms.ModelForm):
    class Meta:
        model = QuarterlyReport
        fields = ['quarter', 'year', 'work_done', 'progress', 'challenges', 'next_plan']
        widgets = {
            'work_done': forms.Textarea(attrs={'rows': 4}),
            'progress': forms.Textarea(attrs={'rows': 4}),
            'challenges': forms.Textarea(attrs={'rows': 3}),
            'next_plan': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default quarter and year based on current date
        from datetime import datetime
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        
        if current_month <= 3:
            default_quarter = 'Q1'
        elif current_month <= 6:
            default_quarter = 'Q2'
        elif current_month <= 9:
            default_quarter = 'Q3'
        else:
            default_quarter = 'Q4'
            
        if not self.instance.pk:  # Only for new instances
            self.fields['quarter'].initial = default_quarter
            self.fields['year'].initial = current_year