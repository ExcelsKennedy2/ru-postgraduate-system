from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from assessments.models import Submission
from chair.models import SupervisorReassignment
from notifications.models import Notification
from pipeline.models import Milestone
from students.models import PresentationBooking, QuarterlyReport, Student
from users.models import User


def _initials(user):
    full_name = user.get_full_name().strip()
    if full_name:
        return "".join(part[0] for part in full_name.split()[:2]).upper()
    return user.username[:2].upper()


def _student_progress(student, today):
    milestones = list(student.milestone_set.all())
    done = sum(1 for milestone in milestones if milestone.status == "done")
    total = len(milestones)
    progress = int(round((done / total) * 100)) if total else 0
    submissions = list(student.submission_set.all())
    last_submission = submissions[0] if submissions else None
    last_active = last_submission.submitted_at if last_submission else None
    inactive_days = (today - last_active.date()).days if last_active else None
    if progress >= 75:
        status_label = "On Track"
        status_badge = "pill-green"
    elif inactive_days is not None and inactive_days >= 45:
        status_label = "Stalled"
        status_badge = "pill-red"
    elif progress >= 40:
        status_label = "Needs Attention"
        status_badge = "pill-amber"
    else:
        status_label = "Needs Attention"
        status_badge = "pill-red"
    return {
        "progress": progress,
        "status_label": status_label,
        "status_badge": status_badge,
        "last_active": last_active,
        "submissions": submissions,
    }


def _chair_redirect(section=""):
    url = reverse("chair_dashboard")
    return f"{url}#{section}" if section else url


@login_required
@user_passes_test(lambda u: u.role in ["chair", "admin", "dean"])
def chair_dashboard(request):
    chair = request.user
    today = timezone.localdate()

    students = list(
        Student.objects.select_related("user", "supervisor")
        .prefetch_related(
            Prefetch("milestone_set", queryset=Milestone.objects.order_by("date", "id")),
            Prefetch("submission_set", queryset=Submission.objects.order_by("-submitted_at")),
        )
        .order_by("user__first_name", "user__last_name", "user__username")
    )
    supervisors = list(
        User.objects.filter(role="supervisor")
        .prefetch_related(
            Prefetch(
                "supervised_students",
                queryset=Student.objects.select_related("user").prefetch_related(
                    Prefetch("milestone_set", queryset=Milestone.objects.order_by("date", "id")),
                    Prefetch("submission_set", queryset=Submission.objects.order_by("-submitted_at")),
                ),
            )
        )
        .order_by("first_name", "last_name", "username")
    )
    submissions = list(
        Submission.objects.select_related("student__user", "student__supervisor", "reviewed_by").order_by("-submitted_at")
    )
    reports = list(QuarterlyReport.objects.select_related("student__user").order_by("-submitted_at"))
    bookings = list(
        PresentationBooking.objects.select_related("student__user")
        .filter(date__gte=timezone.now())
        .order_by("date")[:5]
    )
    notifications = list(Notification.objects.filter(user=chair).order_by("-created_at")[:5])

    student_rows = []
    at_risk_rows = []
    programme_map = defaultdict(list)
    progress_cache = {}

    for student in students:
        summary = _student_progress(student, today)
        progress_cache[student.id] = summary
        student_rows.append(
            {
                "student": student,
                "name": student.user.get_full_name() or student.user.username,
                "initials": _initials(student.user),
                "programme": student.programme,
                "supervisor_name": student.supervisor.get_full_name() if student.supervisor else "Unassigned",
                "progress": summary["progress"],
                "status_label": summary["status_label"],
                "status_badge": summary["status_badge"],
            }
        )
        programme_map[student.programme].append(summary["progress"])
        if summary["progress"] < 50:
            at_risk_rows.append(
                {
                    "name": student.user.get_full_name() or student.user.username,
                    "programme": student.programme,
                    "progress": summary["progress"],
                    "risk_factor": "Low milestone completion",
                    "supervisor_name": student.supervisor.get_full_name() if student.supervisor else "Unassigned",
                }
            )

    supervisor_rows = []
    overloaded_supervisors = []
    for supervisor in supervisors:
        assigned_students = list(supervisor.supervised_students.all())
        student_count = len(assigned_students)
        avg_progress = int(round(sum(progress_cache[s.id]["progress"] for s in assigned_students) / student_count)) if student_count else 0
        reviewed_count = sum(
            1
            for student in assigned_students
            for submission in progress_cache[student.id]["submissions"]
            if submission.status in {"reviewed", "approved"}
        )
        rating = round(min(5.0, 3.0 + (avg_progress / 50)), 1) if student_count else 0
        if avg_progress >= 75:
            status_label = "Excellent"
            status_badge = "pill-amber"
        elif avg_progress >= 60:
            status_label = "Good"
            status_badge = "pill-green"
        else:
            status_label = "Fair"
            status_badge = "pill-orange"
        supervisor_rows.append(
            {
                "user": supervisor,
                "initials": _initials(supervisor),
                "student_count": student_count,
                "avg_progress": avg_progress,
                "rating": rating,
                "reviewed_count": reviewed_count,
                "status_label": status_label,
                "status_badge": status_badge,
                "is_overloaded": student_count > 12,
            }
        )
        if student_count > 12:
            overloaded_supervisors.append(supervisor)

    supervisor_rows.sort(key=lambda row: (-row["avg_progress"], row["user"].get_full_name() or row["user"].username))
    at_risk_rows.sort(key=lambda row: row["progress"])

    programme_stats = []
    for programme, values in sorted(programme_map.items()):
        avg_progress = int(round(sum(values) / len(values))) if values else 0
        programme_stats.append(
            {
                "name": programme,
                "student_count": len(values),
                "avg_progress": avg_progress,
                "duration_text": f"Avg. milestone completion {avg_progress}%",
                "progress_color": "var(--green)" if avg_progress >= 85 else "var(--navy)",
            }
        )

    pending_approvals = []
    for submission in submissions:
        if submission.status in {"submitted", "pending", "revision"} and submission.chair_status == "pending":
            pending_approvals.append(
                {
                    "id": submission.id,
                    "student_name": submission.student.user.get_full_name() or submission.student.user.username,
                    "request_type": "Submission Review",
                    "details": f"{submission.student.programme} - {submission.title}",
                    "submitted_label": submission.submitted_at.strftime("%d %b"),
                    "priority_label": "High" if submission.status == "revision" else "Medium",
                    "priority_badge": "pill-red" if submission.status == "revision" else "pill-amber",
                }
            )
    pending_approvals = pending_approvals[:8]

    issues_count = len(at_risk_rows) + len(overloaded_supervisors)
    alerts = [
        {
            "icon": "Student Progress Review",
            "description": f"{len(at_risk_rows)} students are below the 50% progress threshold",
            "action_class": "alert-action-red",
            "action_text": "Review Now ->",
            "icon_style": "background:var(--red-dim)",
            "symbol": "!",
        },
        {
            "icon": "Supervisor Overload",
            "description": f"{len(overloaded_supervisors)} supervisors are above the suggested load limit",
            "action_class": "alert-action-amber",
            "action_text": "Rebalance Load ->",
            "icon_style": "background:var(--amber-dim)",
            "symbol": "@",
        },
        {
            "icon": "Pending Approvals",
            "description": f"{len(pending_approvals)} items are awaiting chair action",
            "action_class": "alert-action-blue",
            "action_text": "View All ->",
            "icon_style": "background:var(--blue-dim)",
            "symbol": "+",
        },
        {
            "icon": "Quarterly Reports",
            "description": f"{sum(1 for report in reports if report.status == 'reviewed')} reports have already been reviewed",
            "action_class": "alert-action-green",
            "action_text": "View Details ->",
            "icon_style": "background:var(--green-dim)",
            "symbol": "*",
        },
    ]

    report_archive = [
        {
            "title": "Quarterly Report Summary",
            "type": "Quarterly",
            "generated": reports[0].submitted_at if reports else None,
            "scope": f"{len(reports)} student reports",
        },
        {
            "title": "Supervisor Load Distribution",
            "type": "Operational",
            "generated": timezone.now(),
            "scope": f"{len(supervisor_rows)} supervisors",
        },
        {
            "title": "At-Risk Student Intervention Report",
            "type": "Ad hoc",
            "generated": timezone.now(),
            "scope": f"{len(at_risk_rows)} students",
        },
    ]

    completion_rate = int(round(sum(row["progress"] for row in student_rows) / len(student_rows))) if student_rows else 0
    chair_name = chair.get_full_name() or chair.username
    department_name = programme_stats[0]["name"] if programme_stats else "Postgraduate Department"

    context = {
        "chair": chair,
        "chair_name": chair_name,
        "chair_email": chair.email,
        "chair_initials": _initials(chair),
        "chair_staff_id": f"CHR/{chair.id:04d}",
        "chair_role_title": "Department Chair",
        "department_name": department_name,
        "notifications": notifications,
        "stats": {
            "pending_approvals": len(pending_approvals),
            "at_risk_students": len(at_risk_rows),
            "active_supervisors": len([row for row in supervisor_rows if row["student_count"] > 0]),
            "issues": issues_count,
            "reports_generated": len(reports),
            "completion_rate": completion_rate,
        },
        "supervisor_rows": supervisor_rows,
        "supervisors": supervisors,
        "alerts": alerts,
        "upcoming_meetings": bookings,
        "programme_stats": programme_stats,
        "student_rows": student_rows,
        "at_risk_rows": at_risk_rows,
        "pending_approvals": pending_approvals,
        "report_archive": report_archive,
        "analytics": {
            "phd_completion": next((item["avg_progress"] for item in programme_stats if "PhD" in item["name"]), completion_rate),
            "masters_completion": next((item["avg_progress"] for item in programme_stats if "MSc" in item["name"] or "Masters" in item["name"]), completion_rate),
            "avg_time": "N/A",
            "dropout_rate": 0,
            "progress_by_programme": programme_stats,
            "satisfaction": round(sum(row["rating"] for row in supervisor_rows) / len(supervisor_rows), 1) if supervisor_rows else 0,
            "review_timeliness": int(round((sum(row["reviewed_count"] for row in supervisor_rows) / max(len(submissions), 1)) * 100)) if submissions else 0,
            "approval_rate": int(round((sum(1 for submission in submissions if submission.status == "approved") / max(len(submissions), 1)) * 100)) if submissions else 0,
        },
    }
    return render(request, 'chair/chair.html', context)


@login_required
@user_passes_test(lambda u: u.role in ["chair", "admin", "dean"])
def chair_approve_request(request, submission_id):
    if request.method != "POST":
        return redirect(_chair_redirect("view-approvals"))

    submission = get_object_or_404(Submission.objects.select_related("student__user"), pk=submission_id)
    action = request.POST.get("action")

    if action not in {"approve", "defer"}:
        messages.error(request, "Invalid approval action.")
        return redirect(_chair_redirect("view-approvals"))

    submission.reviewed_by = request.user
    submission.reviewed_at = timezone.now()
    if action == "approve":
        submission.chair_status = "approved"
        submission.status = "approved"
        messages.success(request, "Request approved.")
    else:
        submission.chair_status = "deferred"
        submission.status = "pending"
        messages.success(request, "Request deferred.")
    submission.save(update_fields=["chair_status", "status", "reviewed_by", "reviewed_at"])
    return redirect(_chair_redirect("view-approvals"))


@login_required
@user_passes_test(lambda u: u.role in ["chair", "admin", "dean"])
def chair_reassign_students(request):
    if request.method != "POST":
        return redirect(_chair_redirect("view-faculty"))

    new_supervisor_id = request.POST.get("new_supervisor_id")
    student_ids = request.POST.getlist("student_ids")
    reason = request.POST.get("reason", "").strip()

    if not new_supervisor_id or not student_ids or not reason:
        messages.error(request, "Supervisor, students, and reassignment reason are required.")
        return redirect(_chair_redirect("view-faculty"))

    new_supervisor = get_object_or_404(User, pk=new_supervisor_id, role="supervisor")
    students = list(Student.objects.select_related("supervisor", "user").filter(pk__in=student_ids))

    if not students:
        messages.error(request, "No students selected for reassignment.")
        return redirect(_chair_redirect("view-faculty"))

    for student in students:
        SupervisorReassignment.objects.create(
            student=student,
            previous_supervisor=student.supervisor,
            new_supervisor=new_supervisor,
            reason=reason,
            reassigned_by=request.user,
        )
        student.supervisor = new_supervisor
        student.save(update_fields=["supervisor"])

    messages.success(request, f"{len(students)} student(s) reassigned successfully.")
    return redirect(_chair_redirect("view-faculty"))
