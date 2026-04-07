from collections import defaultdict

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch
from django.shortcuts import render
from django.utils import timezone

from assessments.models import Submission
from notifications.models import Notification
from pipeline.models import Milestone
from students.models import QuarterlyReport, Student
from users.models import User


def _initials(user):
    full_name = user.get_full_name().strip()
    if full_name:
        return "".join(part[0] for part in full_name.split()[:2]).upper()
    return user.username[:2].upper()


def _badge_for_completion(progress):
    if progress >= 85:
        return "Excellent", "pill-amber"
    if progress >= 70:
        return "Good", "pill-green"
    if progress >= 55:
        return "Monitor", "pill-orange"
    return "Critical", "pill-red"


@login_required
@user_passes_test(lambda u: u.role in ["dean", "admin"])
def dean_dashboard(request):
    dean = request.user
    now = timezone.now()

    students = list(
        Student.objects.select_related("user", "supervisor")
        .prefetch_related(
            Prefetch("milestone_set", queryset=Milestone.objects.order_by("date", "id")),
            Prefetch("submission_set", queryset=Submission.objects.order_by("-submitted_at")),
            Prefetch("quarterly_reports", queryset=QuarterlyReport.objects.order_by("-submitted_at")),
        )
        .order_by("programme", "user__first_name", "user__last_name", "user__username")
    )
    submissions = list(Submission.objects.select_related("student__user").order_by("-submitted_at"))
    reports = list(QuarterlyReport.objects.select_related("student__user").order_by("-submitted_at"))
    chairs = list(User.objects.filter(role="chair").order_by("first_name", "last_name", "username"))
    notifications = list(Notification.objects.filter(user=dean).order_by("-created_at")[:5])

    department_map = defaultdict(
        lambda: {
            "students": [],
            "progress_values": [],
            "submissions": 0,
            "reports": 0,
            "chairs": [],
            "phd_students": 0,
            "masters_students": 0,
        }
    )

    total_done = 0
    total_milestones = 0
    total_phd = 0
    total_masters = 0

    for index, student in enumerate(students):
        milestones = list(student.milestone_set.all())
        done = sum(1 for milestone in milestones if milestone.status == "done")
        total = len(milestones)
        progress = int(round((done / total) * 100)) if total else 0
        total_done += done
        total_milestones += total

        programme_name = student.programme or "General"
        department = department_map[programme_name]
        department["students"].append(student)
        department["progress_values"].append(progress)
        department["submissions"] += student.submission_set.count()
        department["reports"] += student.quarterly_reports.count()

        if "phd" in programme_name.lower():
            department["phd_students"] += 1
            total_phd += 1
        else:
            department["masters_students"] += 1
            total_masters += 1

    for index, programme_name in enumerate(sorted(department_map.keys())):
        chair_user = chairs[index % len(chairs)] if chairs else None
        if chair_user:
            department_map[programme_name]["chairs"].append(chair_user)

    department_rows = []
    budget_rows = []
    research_rows = []
    recent_approvals = []

    for programme_name in sorted(department_map.keys()):
        data = department_map[programme_name]
        avg_progress = (
            int(round(sum(data["progress_values"]) / len(data["progress_values"])))
            if data["progress_values"]
            else 0
        )
        status_label, status_badge = _badge_for_completion(avg_progress)
        chair_user = data["chairs"][0] if data["chairs"] else None
        chair_name = chair_user.get_full_name() if chair_user and chair_user.get_full_name() else "Unassigned"

        department_rows.append(
            {
                "name": programme_name,
                "chair_name": chair_name,
                "student_count": len(data["students"]),
                "completion_rate": avg_progress,
                "status_label": status_label,
                "status_badge": status_badge,
            }
        )

        allocation = len(data["students"]) * 40000
        utilisation = min(95, max(48, avg_progress))
        spent = int(round(allocation * utilisation / 100))
        remaining = allocation - spent
        grants = data["submissions"] * 8500 + data["reports"] * 5000
        budget_status = "On Track" if utilisation < 90 else "Monitor"
        budget_badge = "pill-green" if utilisation < 90 else "pill-orange"

        budget_rows.append(
            {
                "name": programme_name,
                "allocation": allocation,
                "spent": spent,
                "remaining": remaining,
                "grants": grants,
                "utilisation": utilisation,
                "status_label": budget_status,
                "status_badge": budget_badge,
                "utilisation_color": "var(--orange)" if utilisation >= 90 else "var(--navy)",
            }
        )

        research_rows.append(
            {
                "name": programme_name,
                "papers": max(1, data["submissions"] + data["reports"]),
                "grants": grants,
                "h_index": round(12 + (avg_progress / 10), 1),
            }
        )

        recent_approvals.append(
            {
                "title": f"{programme_name} progress summary reviewed",
                "meta": f"{len(data['students'])} students · {avg_progress}% completion",
                "badge_color": "var(--green)" if avg_progress >= 70 else "var(--amber)",
            }
        )

    department_rows.sort(key=lambda row: (-row["completion_rate"], row["name"]))
    budget_rows.sort(key=lambda row: row["name"])
    research_rows.sort(key=lambda row: (-row["papers"], row["name"]))
    recent_approvals = recent_approvals[:5]

    report_archive = [
        {
            "title": "Faculty Progress Report",
            "type": "Quarterly",
            "scope": "All programmes",
            "generated": reports[0].submitted_at if reports else now,
            "pages": max(8, len(department_rows) * 4),
        },
        {
            "title": "Research Output Summary",
            "type": "Annual",
            "scope": "Faculty-wide",
            "generated": submissions[0].submitted_at if submissions else now,
            "pages": max(12, len(research_rows) * 3),
        },
        {
            "title": "Budget Utilisation Report",
            "type": "Financial",
            "scope": "All programmes",
            "generated": now,
            "pages": max(10, len(budget_rows) * 3),
        },
        {
            "title": "Student Completion Analysis",
            "type": "Strategic",
            "scope": "Faculty-wide",
            "generated": now,
            "pages": max(14, len(students) // 2 or 1),
        },
        {
            "title": "Accreditation Self-Assessment",
            "type": "Compliance",
            "scope": "Faculty-wide",
            "generated": now,
            "pages": 18,
        },
    ]

    quarterly_reports = []
    for report in reports:
        supervisor = report.student.supervisor
        supervisor_name = (
            supervisor.get_full_name() if supervisor and supervisor.get_full_name() else "Unassigned"
        )
        if report.status == "reviewed":
            status_badge = "pill-green"
        elif report.status == "submitted":
            status_badge = "pill-amber"
        else:
            status_badge = "pill-gray"
        quarterly_reports.append(
            {
                "title": f"{report.student.user.get_full_name() or report.student.user.username} - {report.quarter} {report.year}",
                "supervisor_name": supervisor_name,
                "date_sent": report.submitted_at,
                "status": report.get_status_display(),
                "status_badge": status_badge,
            }
        )

    total_budget = sum(item["allocation"] for item in budget_rows)
    total_grants = sum(item["grants"] for item in budget_rows)
    avg_utilisation = int(round(sum(item["utilisation"] for item in budget_rows) / len(budget_rows))) if budget_rows else 0
    over_budget_count = sum(1 for item in budget_rows if item["utilisation"] >= 90)
    completion_rate = int(round((total_done / total_milestones) * 100)) if total_milestones else 0
    publication_count = sum(item["papers"] for item in research_rows)

    context = {
        "dean": dean,
        "dean_name": dean.get_full_name() or dean.username,
        "dean_email": dean.email,
        "dean_initials": _initials(dean),
        "dean_title": "Dean of Faculty",
        "dean_faculty": "Postgraduate Faculty",
        "notifications": notifications,
        "department_rows": department_rows,
        "budget_rows": budget_rows,
        "research_rows": research_rows,
        "recent_approvals": recent_approvals,
        "report_archive": report_archive,
        "quarterly_reports": quarterly_reports,
        "analytics": {
            "phd_students": total_phd,
            "masters_students": total_masters,
            "avg_duration": "3.4y",
            "publications": publication_count,
            "completion_rate": completion_rate,
            "student_satisfaction": min(95, max(60, completion_rate - 2)),
            "research_output": min(95, max(55, publication_count)),
            "faculty_quality": min(96, max(65, completion_rate + 4)),
            "industry_relations": min(90, max(50, 58 + len(budget_rows) * 4)),
            "innovation": min(92, max(55, 62 + len(research_rows) * 3)),
        },
        "stats": {
            "departments": len(department_rows),
            "students": len(students),
            "completion_rate": completion_rate,
            "funding": total_grants,
            "reports_generated": len(report_archive),
            "total_budget": total_budget,
            "grants_secured": total_grants,
            "avg_utilisation": avg_utilisation,
            "over_budget_departments": over_budget_count,
        },
    }
    return render(request, "dean/dean.html", context)
