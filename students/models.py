from django.db import models
from users.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
    
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    student_number = models.CharField(max_length=50)
    programme = models.CharField(max_length=100)

    supervisor_name = models.CharField(max_length=100)
    supervisor_email = models.EmailField()

    def __str__(self):
        return self.user.username
    
class PresentationBooking(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE, related_name="bookings")
    title = models.CharField(max_length=255)  # e.g., "Chapter 4 Presentation"
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ("pending", "Pending Confirmation"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    def clean(self):
        # Ensure booking is at least 7 days in advance
        if self.date < timezone.now() + timezone.timedelta(days=7):
            raise ValidationError("You must book at least 7 days in advance.")

    def __str__(self):
        return f"{self.title} — {self.student.user.username} on {self.date.strftime('%Y-%m-%d %H:%M')}"

class QuarterlyReport(models.Model):
    QUARTER_CHOICES = [
        ('Q1', 'Q1 (Jan-Mar)'),
        ('Q2', 'Q2 (Apr-Jun)'),
        ('Q3', 'Q3 (Jul-Sep)'),
        ('Q4', 'Q4 (Oct-Dec)'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="quarterly_reports")
    quarter = models.CharField(max_length=2, choices=QUARTER_CHOICES)
    year = models.IntegerField()
    work_done = models.TextField()
    progress = models.TextField()
    challenges = models.TextField(blank=True, null=True)
    supervisor_feedback = models.TextField(blank=True, null=True)
    next_plan = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_late = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'quarter', 'year')

    def save(self, *args, **kwargs):
        # Calculate if late
        from datetime import datetime
        quarter_end_dates = {
            'Q1': (self.year, 3, 31),
            'Q2': (self.year, 6, 30),
            'Q3': (self.year, 9, 30),
            'Q4': (self.year, 12, 31),
        }
        end_year, end_month, end_day = quarter_end_dates[self.quarter]
        quarter_end = datetime(end_year, end_month, end_day)
        self.is_late = self.submitted_at.date() > quarter_end.date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.user.username} - {self.quarter} {self.year}"
