from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
import uuid

class User(AbstractUser):
    ROLE_CHOICES = (
        ("student", "Student"),
        ("supervisor", "Supervisor"),
        ("admin", "Admin"),
        ("dean", "Dean"),
        ("chair", "Chair"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # NEW FIELD
    unique_id = models.CharField(max_length=50, unique=True, help_text="Admission Number for students or Staff ID for staff", editable=False)
    def save(self, *args, **kwargs):
        if not self.unique_id:
            self.unique_id = f"USR-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)