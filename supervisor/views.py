from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from assessments.forms import FeedbackForm
from students.models import QuarterlyReport

# Create your views here.
def home(request):
    feedback_form = FeedbackForm()
    return render(request, 'supervisor/supervisor.html', {'feedback_form': feedback_form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def review_quarterly_report(request, pk):
    report = get_object_or_404(QuarterlyReport, pk=pk)
    if request.method == 'POST':
        report.status = 'reviewed'
        report.save()
        messages.success(request, 'Report marked as reviewed.')
        return redirect('supervisor_dashboard')  # Assuming there's a supervisor dashboard
    return render(request, 'supervisor/review_report.html', {'report': report})