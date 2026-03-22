from django.db import models
from students.models import Student
from pipeline.models import PipelineStage

class Submission(models.Model):
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('revision', 'Needs Revision'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    chapter = models.CharField(max_length=50, blank=True, null=True)
    file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    # score = models.IntegerField(null=True, blank=True)
    stage = models.CharField(max_length=50, choices=PipelineStage.choices, default="concept_note")

    def __str__(self):
        return self.title
    
class Feedback(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    comment = models.TextField()
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)