from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from students.models import Student
from .models import Submission, Feedback
from pipeline.models import Milestone

@login_required
def submit_work(request):
    if request.method == "POST":
        student = Student.objects.get(user=request.user)

        title = request.POST.get("title")
        file = request.FILES.get("file")
        stage = request.POST.get("stage")

        Submission.objects.create(
            student=student,
            title=title,
            file=file,
            stage=stage,
            status="pending"
        )

        return redirect("/students/dashboard/")
    
from django.shortcuts import get_object_or_404

@login_required
def give_feedback(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)

    if request.method == "POST":
        comment = request.POST.get("comment")
        score = request.POST.get("score")

        Feedback.objects.create(
            submission=submission,
            comment=comment,
            score=score
        )

        return redirect("/staff/dashboard/")