from django.db import models
from students.models import Student


class FinanceRecord(models.Model):
    STATUS_CHOICES = [
        ("approved", "Approved"),
        ("pending", "Pending"),
        ("rejected", "Rejected"),
    ]

    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="finance_record")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    reference = models.CharField(max_length=100, unique=True)
    comments = models.TextField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.status}"