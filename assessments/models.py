from django.db import models
from users.models import User
from students.models import Student
from pipeline.models import PipelineStage

class Submission(models.Model):
    TYPE_CHOICES = [
        ('concept_note', 'Concept Note'),
        ('proposal_draft', 'Proposal Draft'),
        ('proposal_final', 'Proposal Final'),
        ('chapter_draft', 'Chapter Draft'),
        ('chapter_revision', 'Chapter Revision'),
        ('full_thesis_draft', 'Full Thesis Draft'),
        ('final_thesis_submission', 'Final Thesis Submission'),
        ('presentation_slides', 'Presentation Slides'),
        ('research_paper', 'Research Paper'),
        ('progress_report', 'Progress Report'),
        ('dataset_appendices', 'Dataset / Appendices'),
    ]

    CHAPTER_CHOICES = [
        ('chapter_1', 'Chapter 1: Introduction'),
        ('chapter_2', 'Chapter 2: Literature Review'),
        ('chapter_3', 'Chapter 3: Methodology'),
        ('chapter_4', 'Chapter 4: Data Analysis'),
        ('chapter_5', 'Chapter 5: Discussion'),
        ('chapter_6', 'Chapter 6: Conclusion & Recommendations'),
        ('all_chapters', 'All Chapters'),
        ('proposal_document', 'Proposal Document'),
        ('not_applicable', 'Not Applicable'),
    ]

    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('revision', 'Needs Revision'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='chapter_draft')
    chapter = models.CharField(max_length=50, choices=CHAPTER_CHOICES, default='not_applicable', blank=True, null=True)
    file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    notes = models.TextField(blank=True, null=True)
    stage = models.CharField(max_length=50, choices=PipelineStage.choices, default="concept_note")

    def __str__(self):
        return self.title
    
class Feedback(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedback_given')
    comment = models.TextField()
    score = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)