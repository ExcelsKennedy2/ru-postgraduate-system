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
