# import json
# from urllib import request

# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from erp_integration.services import get_finance_clearance
# from students.models import Student
# from assessments.models import Submission, Feedback
# from pipeline.models import Milestone
# from notifications.models import Notification
# from django.shortcuts import get_object_or_404
# from pipeline.models import StudentProgress
# from erp_integration.services import get_finance_clearance
# from datetime import timedelta
# from django.utils import timezone
# from django.db.models import Avg


# # @login_required
# # def student_dashboard(request):
# #     # student = Student.objects.get(user=request.user)
# #     student = get_object_or_404(Student, user=request.user)
# #     submissions = Submission.objects.filter(student=student)
# #     feedbacks = Feedback.objects.filter(submission__student=student)
# #     milestones = Milestone.objects.filter(student=student)
# #     # notifications = Notification.objects.filter(student=student).order_by('-created_at')[:5]
# #     notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
# #     progress = StudentProgress.objects.filter(student=student).first()

# #     context = {
# #         'student': student,
# #         'submissions': submissions,
# #         'feedbacks': feedbacks,
# #         'milestones': milestones,
# #         'notifications': notifications,
# #         'pending_tasks': milestones.filter(status='upcoming').count(),
# #         'completed_milestones': milestones.filter(status='done').count(),
# #         'progress': progress,
# #     }

# #     return render(request, 'students/student.html', context)

# # @login_required
# # def student_dashboard(request):
# #     student = get_object_or_404(Student, user=request.user)
# #     submissions = Submission.objects.filter(student=student)
# #     feedbacks = Feedback.objects.filter(submission__student=student)
# #     milestones = Milestone.objects.filter(student=student)
# #     notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
# #     progress = StudentProgress.objects.filter(student=student).first()
# #     # Get the index of the active step
# #     active_step = next((step for step in pipeline_steps if step['status'] == 'active'), None)
# #     active_index = pipeline_steps.index(active_step) + 1 if active_step else 0

# #     # Define the pipeline steps
# #     step_titles = [
# #         "Concept Note",
# #         "Proposal Seminar",
# #         "Ethics/NACOSTI",
# #         "Data & Analysis",
# #         "Notice of Submission",
# #         "Thesis Exam",
# #         "Oral Defense",
# #         "Graduation"
# #     ]

# #     pipeline_steps = []
    
# #     current_stage = progress.stage if progress else 0  # assuming StudentProgress.stage is an integer 1-8

# #     for index, title in enumerate(step_titles, start=1):
# #         if index < current_stage:
# #             status = "done"
# #         elif index == current_stage:
# #             status = "active"
# #         else:
# #             status = "pending"
# #         pipeline_steps.append({"title": title, "status": status})

# #     context = {
# #         'student': student,
# #         "active_step": active_step,
# #         "active_index": active_index,
# #         'submissions': submissions,
# #         'feedbacks': feedbacks,
# #         'milestones': milestones,
# #         'notifications': notifications,
# #         'pending_tasks': milestones.filter(status='upcoming').count(),
# #         'completed_milestones': milestones.filter(status='done').count(),
# #         'progress': progress,
# #         'pipeline_steps': pipeline_steps,  # dynamic pipeline
# #     }

# #     return render(request, 'students/student.html', context)

# # @login_required
# # def student_dashboard(request):
# #     student = get_object_or_404(Student, user=request.user)
# #     submissions = Submission.objects.filter(student=student)
# #     feedbacks = Feedback.objects.filter(submission__student=student)
# #     milestones = Milestone.objects.filter(student=student)
# #     notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
# #     progress = StudentProgress.objects.filter(student=student).first()
# #     # Find first step that is not done
# #     in_progress_step = next((step for step in pipeline_steps if step['status'] != 'done'), None)
# #     in_progress_text = "In Progress" if in_progress_step else "Completed"

# #     # -----------------------------
# #     # Define pipeline steps here
# #     # -----------------------------
# #     pipeline_steps = [
# #         {"title": "Concept Note", "status": "done"},
# #         {"title": "Proposal Seminar", "status": "done"},
# #         {"title": "Ethics/NACOSTI", "status": "done"},
# #         {"title": "Data & Analysis", "status": "active"},
# #         {"title": "Notice of Submission", "status": "pending"},
# #         {"title": "Thesis Exam", "status": "pending"},
# #         {"title": "Oral Defense", "status": "pending"},
# #         {"title": "Graduation", "status": "pending"},
# #     ]

# #     # Get active step info
# #     active_step = next((step for step in pipeline_steps if step['status'] == 'active'), None)
# #     active_index = pipeline_steps.index(active_step) + 1 if active_step else 0

# #     context = {
# #         'student': student,
# #         'submissions': submissions,
# #         'feedbacks': feedbacks,
# #         'milestones': milestones,
# #         'notifications': notifications,
# #         'pending_tasks': milestones.filter(status='upcoming').count(),
# #         'completed_milestones': milestones.filter(status='done').count(),
# #         'progress': progress,
# #         'pipeline_steps': pipeline_steps,
# #         'active_step': active_step,
# #         'active_index': active_index,
# #         'in_progress_text': in_progress_text,  # <-- new variable
# #     }

# #     return render(request, 'students/student.html', context)

# @login_required
# def student_dashboard(request):
#     student = get_object_or_404(Student, user=request.user)
#     submissions = Submission.objects.filter(student=student)
#     feedbacks = Feedback.objects.filter(submission__student=student)
#     milestones = Milestone.objects.filter(student=student)
#     notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
#     progress = StudentProgress.objects.filter(student=student).first()
    

#     scores = {
#         "Literature Review": feedbacks.filter(category="literature").aggregate(avg=Avg("score"))["avg"] or 0,
#         "Methodology": feedbacks.filter(category="methodology").aggregate(avg=Avg("score"))["avg"] or 0,
#         "Data Analysis": feedbacks.filter(category="analysis").aggregate(avg=Avg("score"))["avg"] or 0,
#         "Writing Quality": feedbacks.filter(category="writing").aggregate(avg=Avg("score"))["avg"] or 0,
#     }

#     # ✅ STEP 1: DEFINE pipeline_steps FIRST
#     # pipeline_steps = [
#     #     {"title": "Concept Note", "status": "done"},
#     #     {"title": "Proposal Seminar", "status": "done"},
#     #     {"title": "Ethics/NACOSTI", "status": "done"},
#     #     {"title": "Data & Analysis", "status": "active"},
#     #     {"title": "Notice of Submission", "status": "pending"},
#     #     {"title": "Thesis Exam", "status": "pending"},
#     #     {"title": "Oral Defense", "status": "pending"},
#     #     {"title": "Graduation", "status": "pending"},
#     # ]

#     # pipeline_steps = []

#     # # Define the correct order (VERY IMPORTANT)
#     # pipeline_order = [
#     #     "Concept Note",
#     #     "Proposal Seminar",
#     #     "Ethics/NACOSTI",
#     #     "Data & Analysis",
#     #     "Notice of Submission",
#     #     "Thesis Exam",
#     #     "Oral Defense",
#     #     "Graduation",
#     # ]

#     # # Convert milestones queryset to dict for quick lookup
#     # milestone_dict = {m.title: m for m in milestones}

#     # for stage in pipeline_order:
#     #     milestone = milestone_dict.get(stage)

#     #     if milestone:
#     #         if milestone.status == "done":
#     #             status = "done"
#     #         elif milestone.status in ["in_progress", "ongoing"]:
#     #             status = "active"
#     #         else:
#     #             status = "pending"
#     #     else:
#     #         status = "pending"

#     #     pipeline_steps.append({
#     #         "title": stage,
#     #         "status": status,
#     #     })
#     pipeline_steps = []
#     pipeline_order = [
#         "Concept Note",
#         "Proposal Seminar",
#         "Ethics/NACOSTI",
#         "Data & Analysis",
#         "Notice of Submission",
#         "Thesis Exam",
#         "Oral Defense",
#         "Graduation",
#     ]

#     milestone_dict = {m.title: m for m in milestones}

#     has_active = False

#     for stage in pipeline_order:
#         milestone = milestone_dict.get(stage)

#         if milestone:
#             if milestone.status == "done":
#                 status = "done"
#             elif milestone.status in ["in_progress", "ongoing"] and not has_active:
#                 status = "active"
#                 has_active = True
#             else:
#                 status = "pending"
#         else:
#             status = "pending"

#         pipeline_steps.append({
#             "title": stage,
#             "status": status,
#         })

#     # fallback if no active stage
#     if not has_active:
#         for step in pipeline_steps:
#             if step["status"] == "pending":
#                 step["status"] = "active"
#                 break

#     # ✅ STEP 2: NOW use pipeline_steps safely
#     active_step = next((step for step in pipeline_steps if step['status'] == 'active'), None)
#     active_index = pipeline_steps.index(active_step) + 1 if active_step else 0

#     in_progress_step = next((step for step in pipeline_steps if step['status'] != 'done'), None)
#     in_progress_text = "In Progress" if in_progress_step else "Completed"

#     tasks_due_this_week = milestones.filter(
#         status='upcoming'
#     ).count()

#     total_milestones = milestones.count()
#     new_feedback = feedbacks.filter(is_read=False).count()

#     finance = get_finance_clearance(student)

#     # Last 6 months
#     today = timezone.now().date()

#     months = []
#     progress_values = []

#     total = milestones.count()
#     completed = milestones.filter(status="done").count()
#     progress_percent = int((completed / total) * 100) if total else 0

#     for i in range(5, -1, -1):
#         month_date = today - timedelta(days=30 * i)
#         months.append(month_date.strftime("%b"))

#         # simulate growth curve
#         factor = (6 - i) / 6
#         progress_values.append(int(progress_percent * factor))
    
#     import json

#     # Example dynamic data
#     months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]

#     total = milestones.count()
#     completed = milestones.filter(status="done").count()

#     progress_percent = int((completed / total) * 100) if total else 0

#     # simulate monthly growth for now
#     progress_values = [
#         int(progress_percent * 0.2),
#         int(progress_percent * 0.4),
#         int(progress_percent * 0.6),
#         int(progress_percent * 0.8),
#         int(progress_percent * 0.9),
#         progress_percent,
#     ]

#     # Example scores (you can compute from Feedback model later)
#     # scores = {
#     #     "Literature Review": 82,
#     #     "Methodology": 78,
#     #     "Data Analysis": 91,
#     #     "Writing Quality": 86,
#     # }

    

#     # ✅ STEP 3: context
#     context = {
#         'student': student,
#         'submissions': submissions,
#         'feedbacks': feedbacks,
#         'milestones': milestones,
#         'notifications': notifications,
#         'pending_tasks': milestones.filter(status='upcoming').count(),
#         'completed_milestones': milestones.filter(status='done').count(),
#         'progress': progress,
#         'pipeline_steps': pipeline_steps,
#         'active_step': active_step,
#         'active_index': active_index,
#         'in_progress_text': in_progress_text,
#         'tasks_due_this_week': tasks_due_this_week,
#         'total_milestones': total_milestones,
#         'new_feedback': new_feedback,
#         'finance': finance,
#         "months": months,
#         # "progress_data": progress_data,
#         'progress_values': progress_values,
#         'scores_labels': scores_labels,
#         'scores_values': scores_values,
#     }
#     context.update({
#             "months": json.dumps(months),
#             "progress_values": json.dumps(progress_values),
#             "scores_labels": json.dumps(list(scores.keys())),
#             "scores_values": json.dumps(list(scores.values())),
#         })
    
#     scores_labels = json.dumps(list(scores.keys()))
#     scores_values = json.dumps(list(scores.values()))

#     return render(request, 'students/student.html', context)

import json
from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from students.models import Student
from assessments.models import Submission, Feedback
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
    milestones = Milestone.objects.filter(student=student)
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    progress = StudentProgress.objects.filter(student=student).first()

    # -----------------------------
    # 📊 SCORES (Dynamic)
    # -----------------------------
    # scores = {
    #     "Literature Review": feedbacks.filter(category="literature").aggregate(avg=Avg("score"))["avg"] or 0,
    #     "Methodology": feedbacks.filter(category="methodology").aggregate(avg=Avg("score"))["avg"] or 0,
    #     "Data Analysis": feedbacks.filter(category="analysis").aggregate(avg=Avg("score"))["avg"] or 0,
    #     "Writing Quality": feedbacks.filter(category="writing").aggregate(avg=Avg("score"))["avg"] or 0,
    # }
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
    new_feedback = feedbacks.filter(is_read=False).count()

    # -----------------------------
    # 💰 ERP FINANCE
    # -----------------------------
    finance = get_finance_clearance(student)

    supervisor_name = student.supervisor_name
    initials = "".join([part[0] for part in supervisor_name.split()][:2]).upper()

    supervisor = {
        "name": supervisor_name,
        "email": student.supervisor_email,
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
    }
    

    context["circle_offset"] = round(offset, 1)
    context["in_progress_percent"] = int((in_progress / total) * 100) if total else 0
    context["upcoming_percent"] = int((upcoming / total) * 100) if total else 0
    return render(request, "students/student.html", context)


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from assessments.models import Submission

@login_required
def submissions_api(request):
    student = request.user.student
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



import io
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from xhtml2pdf import pisa

from students.models import Student
from assessments.models import Submission, Feedback
from pipeline.models import Milestone, StudentProgress

@login_required
def download_submission(request, submission_id):
    # Get the student and submission
    student = get_object_or_404(Student, user=request.user)
    submission = get_object_or_404(Submission, id=submission_id, student=student)
    feedbacks = Feedback.objects.filter(submission=submission)

    # Render HTML template
    html_string = render_to_string("students/submission_pdf.html", {
        "student": student,
        "submission": submission,
        "feedbacks": feedbacks,
    })

    # Create a PDF file in memory
    pdf_file = io.BytesIO()
    pisa_status = pisa.CreatePDF(src=html_string, dest=pdf_file)

    if pisa_status.err:
        return HttpResponse("We had some errors generating the PDF.", content_type="text/plain")

    pdf_file.seek(0)
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{submission.title}.pdf"'
    return response

@login_required
def download_all_submissions(request):
    student = get_object_or_404(Student, user=request.user)
    submissions = Submission.objects.filter(student=student).order_by('-submitted_at')
    
    all_feedbacks = Feedback.objects.filter(submission__in=submissions).select_related('submission')

    # Render all submissions in a single template
    html_string = render_to_string("students/all_submissions_pdf.html", {
        "student": student,
        "submissions": submissions,
        "feedbacks": all_feedbacks,
    })

    pdf_file = io.BytesIO()
    pisa_status = pisa.CreatePDF(src=html_string, dest=pdf_file)

    if pisa_status.err:
        return HttpResponse("Error generating PDF.", content_type="text/plain")

    pdf_file.seek(0)
    response = HttpResponse(pdf_file, content_type='application/pdf')
    # response['Content-Disposition'] = f'attachment; filename="{student.full_name}_all_reports.pdf"'
    response['Content-Disposition'] = f'attachment; filename="{student.user.get_full_name() or student.user.username}_all_reports.pdf"'
    return response

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import PresentationBooking

@login_required
def book_presentation(request):
    student = request.user.student

    if request.method == "POST":
        title = request.POST.get("title")
        date_str = request.POST.get("date")  # e.g., "2026-04-30T10:00"
        try:
            date = timezone.datetime.fromisoformat(date_str)
            date = timezone.make_aware(date, timezone.get_current_timezone())
        except Exception:
            messages.error(request, "Invalid date format.")
            return redirect("student_dashboard")

        booking = PresentationBooking(student=student, title=title, date=date)
        try:
            booking.full_clean()  # runs the clean() method
            booking.save()
            messages.success(request, "Presentation booked successfully!")
        except ValidationError as e:
            messages.error(request, e.message_dict or e.messages)
        return redirect("student_dashboard")


# import io
# from django.http import HttpResponse
# from reportlab.pdfgen import canvas
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404

# from students.models import Student
# from assessments.models import Submission, Feedback

# @login_required
# def download_submission(request, submission_id):
#     student = get_object_or_404(Student, user=request.user)
#     submission = get_object_or_404(Submission, id=submission_id, student=student)
#     feedbacks = Feedback.objects.filter(submission=submission)

#     buffer = io.BytesIO()
#     p = canvas.Canvas(buffer)

#     # Title
#     p.setFont("Helvetica-Bold", 14)
#     p.drawString(100, 800, f"Submission Report")

#     # Student info
#     p.setFont("Helvetica", 10)
#     p.drawString(100, 780, f"Student: {student.user.get_full_name()}")
#     p.drawString(100, 760, f"Title: {submission.title}")
#     p.drawString(100, 740, f"Type: {submission.type}")

#     y = 700
#     p.drawString(100, y, "Feedback:")
#     y -= 20

#     for fb in feedbacks:
#         p.drawString(100, y, f"- {fb.comment}")
#         y -= 20

#     p.showPage()
#     p.save()

#     buffer.seek(0)
#     return HttpResponse(buffer, content_type='application/pdf')