from django.db import models

class PipelineStage(models.TextChoices):
    CONCEPT = "concept_note"
    PROPOSAL = "proposal"
    DATA_COLLECTION = "data_collection"
    THESIS = "thesis"
    COMPLETED = "completed"


# class StudentProgress(models.Model):
#     student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
#     stage = models.CharField(max_length=50, choices=PipelineStage.choices)
#     updated_at = models.DateTimeField(auto_now=True)

class StudentProgress(models.Model):
    student = models.OneToOneField("students.Student", on_delete=models.CASCADE)
    current_stage = models.CharField(max_length=50, choices=PipelineStage.choices)
    updated_at = models.DateTimeField(auto_now=True)

from django.db import models
from students.models import Student

# class Milestone(models.Model):
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     status = models.CharField(max_length=20)  # done, active, upcoming
#     due_date = models.DateField(null=True, blank=True)

class Milestone(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=[
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('upcoming', 'Upcoming'),
    ])

    date = models.DateField(null=True, blank=True)  # ✅ ADD THIS

    def __str__(self):
        return self.title