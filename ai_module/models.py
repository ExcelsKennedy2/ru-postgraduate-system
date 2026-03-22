from django.db import models

# class Correction(models.Model):
#     student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
#     transcript = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

class Correction(models.Model):
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
    stage = models.CharField(max_length=50, default="concept_note")  # ADD THIS
    transcript = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# class CorrectionItem(models.Model):
#     correction = models.ForeignKey(Correction, on_delete=models.CASCADE, related_name="items")
#     text = models.TextField()
#     severity = models.CharField(max_length=20)  # Critical, Major, Minor
#     is_resolved = models.BooleanField(default=False)

class CorrectionItem(models.Model):
    correction = models.ForeignKey(Correction, on_delete=models.CASCADE, related_name="items")
    text = models.TextField()
    severity = models.CharField(max_length=20)
    is_resolved = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)  # ADD THIS