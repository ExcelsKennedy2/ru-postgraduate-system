from django.conf import settings
from django.db import models

from students.models import Student


class SupervisorReassignment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="reassignment_history")
    previous_supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="previous_supervisor_reassignments",
    )
    new_supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="new_supervisor_reassignments",
    )
    reason = models.TextField()
    reassigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chair_reassignments_made",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} -> {self.new_supervisor}"
