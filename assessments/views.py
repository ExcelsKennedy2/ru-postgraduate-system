from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from students.models import Student
from .models import Submission, Feedback
from pipeline.models import Milestone
from .forms import SubmissionForm, FeedbackForm

@login_required
def submit_work(request):
    student = Student.objects.get(user=request.user)

    if request.method == "POST":
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = student
            submission.status = 'pending'
            submission.save()
            return redirect("/students/dashboard/")
    else:
        form = SubmissionForm()

    return render(request, 'assessments/submit.html', {'form': form})

from django.shortcuts import get_object_or_404

@login_required
def give_feedback(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/supervisor/dashboard/")
    else:
        form = FeedbackForm()

    return render(request, 'assessments/give_feedback.html', {'form': form})