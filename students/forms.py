from django import forms
from .models import PresentationBooking, QuarterlyReport

class PresentationBookingForm(forms.ModelForm):
    class Meta:
        model = PresentationBooking
        fields = ['title', 'date']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

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