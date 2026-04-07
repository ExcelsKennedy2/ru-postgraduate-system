import json
from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from students.models import Student, PresentationBooking, QuarterlyReport
from assessments.models import Submission, Feedback
from assessments.forms import SubmissionForm
from students.forms import PresentationBookingForm, StudentProfileForm, QuarterlyReportForm
from pipeline.models import Milestone, StudentProgress
from notifications.models import Notification
from erp_integration.services import get_finance_clearance


@login_required
def student_dashboard(request):
    student = get_object_or_404(Student, user=request.user)

    submissions = Submission.objects.filter(student=student)
    # feedbacks = Feedback.objects.filter(submission__student=student)
    feedbacks = Feedback.objects.filter(
        submission__student=student
    ).select_related('submission')

    profile_form = StudentProfileForm(instance=student)
    if request.method == 'POST' and request.POST.get('profile_update'):
        profile_form = StudentProfileForm(request.POST, instance=student)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('student_dashboard')
    milestones = Milestone.objects.filter(student=student)
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    progress = StudentProgress.objects.filter(student=student).first()
    scores = {
        "Literature Review": feedbacks.filter(submission__type="literature").aggregate(avg=Avg("score"))["avg"] or 0,
        "Methodology": feedbacks.filter(submission__type="methodology").aggregate(avg=Avg("score"))["avg"] or 0,
        "Data Analysis": feedbacks.filter(submission__type="analysis").aggregate(avg=Avg("score"))["avg"] or 0,
        "Writing Quality": feedbacks.filter(submission__type="writing").aggregate(avg=Avg("score"))["avg"] or 0,
    }
    scores_labels = json.dumps(list(scores.keys()))
    scores_values = json.dumps([round(v, 1) for v in scores.values()])

    # -----------------------------
    # 📈 PROGRESS CHART
    # -----------------------------
    today = timezone.now().date()

    months = []
    progress_values = []

    total = milestones.count()
    completed = milestones.filter(status="done").count()
    in_progress = milestones.filter(status="in_progress").count()
    upcoming = milestones.filter(status="upcoming").count()
    progress_percent = int((completed / total) * 100) if total else 0
    # progress = StudentProgress.objects.filter(student=student).first()

    for i in range(5, -1, -1):
        month_date = today - timedelta(days=30 * i)
        months.append(month_date.strftime("%b"))

        # Smooth growth simulation
        factor = (6 - i) / 6
        progress_values.append(int(progress_percent * factor))

    months_json = json.dumps(months)
    progress_values_json = json.dumps(progress_values)

    # -----------------------------
    # 📌 PIPELINE
    # -----------------------------
    pipeline_order = [
        "Concept Note",
        "Proposal Seminar",
        "Ethics/NACOSTI",
        "Data & Analysis",
        "Notice of Submission",
        "Thesis Exam",
        "Oral Defense",
        "Graduation",
    ]

    milestone_dict = {m.title: m for m in milestones}
    pipeline_steps = []
    has_active = False

    for stage in pipeline_order:
        milestone = milestone_dict.get(stage)

        if milestone:
            if milestone.status == "done":
                status = "done"
            elif milestone.status in ["in_progress", "ongoing"] and not has_active:
                status = "active"
                has_active = True
            else:
                status = "pending"
        else:
            status = "pending"

        pipeline_steps.append({"title": stage, "status": status})

    if not has_active:
        for step in pipeline_steps:
            if step["status"] == "pending":
                step["status"] = "active"
                break

    active_step = next((s for s in pipeline_steps if s["status"] == "active"), None)
    active_index = pipeline_steps.index(active_step) + 1 if active_step else 0

    # -----------------------------
    # 📊 STATS
    # -----------------------------
    tasks_due_this_week = milestones.filter(status='upcoming').count()
    total_milestones = milestones.count()
    completed_milestones = milestones.filter(status='done').count()
    remaining_milestones = total_milestones - completed_milestones
    new_feedback = feedbacks.filter(is_read=False).count()

    # Calculate GPA and score averages
    current_gpa = round(sum([f.score for f in feedbacks if f.score]) / len([f for f in feedbacks if f.score]), 2) if feedbacks.exists() and any(f.score for f in feedbacks) else 0.0
    avg_score = round(current_gpa * 20, 1) if current_gpa > 0 else 0  # Convert GPA to percentage
    supervisor_rating = min(5.0, round(current_gpa / 20 * 5, 1)) if current_gpa > 0 else 0
    review_count = feedbacks.count()

    # -----------------------------
    # 💰 ERP FINANCE
    # -----------------------------
    finance = get_finance_clearance(student)

    if student.supervisor:
        supervisor_name = student.supervisor.get_full_name() or student.supervisor.username
        supervisor_email = student.supervisor.email
    else:
        supervisor_name = "Assigned Supervisor"
        supervisor_email = "noreply@university.edu"

    initials = "".join([part[0] for part in supervisor_name.split()][:2]).upper()

    supervisor = {
        "name": supervisor_name,
        "email": supervisor_email,
        "initials": initials,
        # If you have role/department stored somewhere else, add here
        "role": "Research Supervisor",
        "department": "Computer Science"
    }
    offset = 213.6 * (1 - progress_percent / 100)
    feedback_items = []

    for f in feedbacks.select_related('submission').order_by('-created_at'):
        if f.score is not None:
            if f.score >= 80:
                status = "approved"
            elif f.score >= 50:
                status = "revision"
            else:
                status = "revision"
        else:
            status = "pending"

        feedback_items.append({
            "title": f.submission.title,
            "chapter": f.submission.chapter,
            "message": f.comment,
            "score": f.score,
            "status": status,
            "date": f.created_at,
            "is_read": f.is_read,
        })
    
    # current stage info
    current_stage_title = active_step["title"] if active_step else "Not started"
    current_stage_number = active_index

    # stage stats (basic for now)
    stage_submissions = submissions.filter(type=current_stage_title).count()
    revision_count = submissions.filter(
        type=current_stage_title,
        status="revision"
    ).count()

    completed_steps = len([s for s in pipeline_steps if s["status"] == "done"])
    current_steps = len([s for s in pipeline_steps if s["status"] == "active"])
    pending_steps = len([s for s in pipeline_steps if s["status"] == "pending"])
    bookings = student.bookings.all().order_by('date')

    

    # -----------------------------
    # 🎯 FINAL CONTEXT
    # -----------------------------
    context = {
        "student": student,
        "submissions": submissions,
        "feedbacks": feedbacks,
        # "milestones": milestones,
        'milestones': milestones.order_by('date'),
        "notifications": notifications,
        "progress": progress,

        # stats
        "pending_tasks": tasks_due_this_week,
        "completed_milestones": completed_milestones,
        "total_milestones": total_milestones,
        "new_feedback": new_feedback,

        # pipeline
        "pipeline_steps": pipeline_steps,
        "active_step": active_step,
        "active_index": active_index,

        # charts
        "months": months_json,
        "progress_values": progress_values_json,
        "scores_labels": scores_labels,
        "scores_values": scores_values,

        # finance
        "finance": finance,

        "supervisor": supervisor,
        "in_progress_milestones": in_progress,
        "upcoming_milestones": upcoming,
        "current_stage": progress.current_stage if progress else None,
        "context_feedbacks": feedback_items,
        "unread_feedback_count": feedbacks.filter(is_read=False).count(),
        "current_stage_title": current_stage_title,
        "current_stage_number": current_stage_number,
        "total_stages": len(pipeline_steps),
        "stage_submissions": stage_submissions,
        "revision_count": revision_count,
        "completed_steps": completed_steps,
        "current_steps": current_steps,
        "pending_steps": pending_steps,
        "bookings": bookings,
        "submission_form": SubmissionForm(),
        "presentation_booking_form": PresentationBookingForm(),
        "student_profile_form": profile_form,
    }
    

    context["circle_offset"] = round(offset, 1)
    context["in_progress_percent"] = int((in_progress / total) * 100) if total else 0
    context["upcoming_percent"] = int((upcoming / total) * 100) if total else 0
    context["remaining_milestones"] = remaining_milestones
    context["in_progress_text"] = f"{in_progress} in progress"
    context["current_gpa"] = current_gpa
    context["avg_score"] = avg_score
    context["supervisor_rating"] = supervisor_rating
    context["review_count"] = review_count
    return render(request, "students/student.html", context)


@login_required
def submissions_api(request):
    student = request.user.student_profile
    subs = Submission.objects.filter(student=student).order_by('-submitted_at')
    
    data = []
    for s in subs:
        feedback = s.feedback_set.order_by('-created_at').first()
        data.append({
            "title": s.title,
            "type": s.type,
            "chapter": s.chapter or '—',
            "submitted": s.submitted_at.strftime("%Y-%m-%d"),
            "supervisor": "Dr. Michael Chen",  # placeholder
            "status": s.get_status_display(),
            "score": feedback.score if feedback else '—',
            "id": s.id
        })
    return JsonResponse({"submissions": data})
    # student = request.user.student  # assuming you have a related Student model
    # subs = Submission.objects.filter(student=student).order_by('-submitted_at')
    
    # data = []
    # for s in subs:
    #     data.append({
    #         "title": s.title,
    #         "type": s.type,
    #         "chapter": s.chapter or '—',
    #         "submitted": s.submitted_at.strftime("%Y-%m-%d"),
    #         # "supervisor": s.supervisor.get_full_name(),
    #         "supervisor": "Dr. Michael Chen",  # placeholder
    #         "status": s.get_status_display(),  # e.g., Approved, Pending, Needs Revision
    #         "score": s.score if s.score is not None else '—',
    #         "id": s.id
    #     })
    # return JsonResponse({"submissions": data})


@login_required
def download_submission(request, submission_id):
    student = get_object_or_404(Student, user=request.user)
    submission = get_object_or_404(Submission, id=submission_id, student=student)
    feedbacks = Feedback.objects.filter(submission=submission)
    return render(request, "students/submission_report.html", {
        "student": student,
        "submission": submission,
        "feedbacks": feedbacks,
    })


@login_required
def download_all_submissions(request):
    student = get_object_or_404(Student, user=request.user)
    submissions = Submission.objects.filter(student=student).order_by('-submitted_at')
    all_feedbacks = Feedback.objects.filter(submission__in=submissions).select_related('submission')
    return render(request, "students/all_submissions_report.html", {
        "student": student,
        "submissions": submissions,
        "feedbacks": all_feedbacks,
    })


@login_required
def book_presentation(request):
    student = request.user.student_profile

    if request.method == "POST":
        form = PresentationBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.student = student
            try:
                booking.full_clean()  # runs the clean() method
                booking.save()
                messages.success(request, "Presentation booked successfully!")
                return redirect('book_presentation')
            except ValidationError as e:
                form.add_error(None, e)
        else:
            messages.error(request, "Form is invalid.")
    else:
        form = PresentationBookingForm()

    bookings = PresentationBooking.objects.filter(student=student).order_by('-date')
    return render(request, 'students/book_presentation.html', {
        'form': form,
        'bookings': bookings,
    })


@login_required
def list_quarterly_reports(request):
    student = get_object_or_404(Student, user=request.user)
    reports = QuarterlyReport.objects.filter(student=student).order_by('-submitted_at')
    return render(request, 'students/quarterly_report_list.html', {'reports': reports})


@login_required
def create_quarterly_report(request):
    student = get_object_or_404(Student, user=request.user)
    if request.method == 'POST':
        form = QuarterlyReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.student = student
            report.save()
            messages.success(request, 'Quarterly report saved as draft.')
            return redirect('list_quarterly_reports')
    else:
        form = QuarterlyReportForm()
    return render(request, 'students/quarterly_report_form.html', {'form': form})


@login_required
def detail_quarterly_report(request, pk):
    student = get_object_or_404(Student, user=request.user)
    report = get_object_or_404(QuarterlyReport, pk=pk, student=student)
    return render(request, 'students/quarterly_report_detail.html', {'report': report})


@login_required
def update_quarterly_report(request, pk):
    student = get_object_or_404(Student, user=request.user)
    report = get_object_or_404(QuarterlyReport, pk=pk, student=student)
    if report.status != 'draft':
        messages.error(request, 'You can only edit draft reports.')
        return redirect('detail_quarterly_report', pk=pk)
    
    if request.method == 'POST':
        form = QuarterlyReportForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            messages.success(request, 'Report updated.')
            return redirect('detail_quarterly_report', pk=pk)
    else:
        form = QuarterlyReportForm(instance=report)
    return render(request, 'students/quarterly_report_form.html', {'form': form, 'report': report})


@login_required
def submit_quarterly_report(request, pk):
    student = get_object_or_404(Student, user=request.user)
    report = get_object_or_404(QuarterlyReport, pk=pk, student=student)
    if report.status == 'draft':
        report.status = 'submitted'
        report.save()
        messages.success(request, 'Report submitted successfully.')
    else:
        messages.error(request, 'Report is not in draft status.')
    return redirect('detail_quarterly_report', pk=pk)