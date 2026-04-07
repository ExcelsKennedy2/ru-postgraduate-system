import math
from collections import defaultdict
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from assessments.forms import FeedbackForm
from assessments.models import Feedback, Submission
from notifications.models import Notification
from pipeline.models import Milestone
from students.models import PresentationBooking, QuarterlyReport, Student


@login_required
@user_passes_test(lambda u: u.role in ["supervisor", "admin", "dean"])
def supervisor_dashboard(request):
    supervisor = request.user
    now = timezone.now()
    today = timezone.localdate()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    if request.method == "POST" and request.POST.get("form_type") == "meeting_action":
        action = request.POST.get("meeting_action", "schedule").strip().lower()
        booking_id = request.POST.get("booking_id")
        student_id = request.POST.get("student_id")
        title = (request.POST.get("title") or "").strip()
        meeting_type = request.POST.get("meeting_type", "in_person")
        notes = (request.POST.get("notes") or "").strip()
        date_value = request.POST.get("date")
        time_value = request.POST.get("time")

        if not student_id or not title or not date_value or not time_value:
            messages.error(request, "Student, date, time, and topic are required.")
            return redirect("supervisor_dashboard")

        student = get_object_or_404(Student, pk=student_id, supervisor=supervisor)

        try:
            meeting_dt = datetime.strptime(f"{date_value} {time_value}", "%Y-%m-%d %H:%M")
            aware_meeting_dt = timezone.make_aware(meeting_dt, timezone.get_current_timezone())
        except ValueError:
            messages.error(request, "Please provide a valid meeting date and time.")
            return redirect("supervisor_dashboard")

        booking = None
        if booking_id:
            booking = get_object_or_404(
                PresentationBooking.objects.select_related("student"),
                pk=booking_id,
                student__supervisor=supervisor,
            )

        if action == "schedule":
            PresentationBooking.objects.create(
                student=student,
                title=title,
                date=aware_meeting_dt,
                meeting_type=meeting_type,
                notes=notes,
                status="pending",
            )
            messages.success(request, "Meeting scheduled and student notified.")
            return redirect("supervisor_dashboard")

        if booking is None:
            messages.error(request, "Meeting record not found.")
            return redirect("supervisor_dashboard")

        booking.student = student
        booking.title = title
        booking.date = aware_meeting_dt
        booking.meeting_type = meeting_type
        booking.notes = notes

        if action == "confirm":
            booking.status = "approved"
            success_message = "Meeting confirmed successfully."
        elif action == "reschedule":
            booking.status = "pending"
            success_message = "Meeting rescheduled successfully."
        elif action == "review":
            success_message = "Meeting details reviewed successfully."
        else:
            success_message = "Meeting updated successfully."

        booking.save()
        messages.success(request, success_message)
        return redirect("supervisor_dashboard")

    students_qs = (
        Student.objects.filter(supervisor=supervisor)
        .select_related("user")
        .prefetch_related(
            Prefetch("milestone_set", queryset=Milestone.objects.order_by("date", "id")),
            Prefetch(
                "submission_set",
                queryset=Submission.objects.select_related("student__user")
                .order_by("-submitted_at")
                .prefetch_related(
                    Prefetch(
                        "feedback_set",
                        queryset=Feedback.objects.select_related("supervisor").order_by("-created_at"),
                    )
                ),
            ),
            Prefetch("bookings", queryset=PresentationBooking.objects.order_by("date")),
            Prefetch("quarterly_reports", queryset=QuarterlyReport.objects.order_by("-submitted_at")),
        )
    )
    submissions_qs = (
        Submission.objects.filter(student__supervisor=supervisor)
        .select_related("student", "student__user")
        .prefetch_related(
            Prefetch(
                "feedback_set",
                queryset=Feedback.objects.select_related("supervisor").order_by("-created_at"),
            )
        )
        .order_by("-submitted_at")
    )
    feedbacks_qs = (
        Feedback.objects.filter(supervisor=supervisor)
        .select_related("submission__student__user")
        .order_by("-created_at")
    )
    reports_qs = (
        QuarterlyReport.objects.filter(student__supervisor=supervisor)
        .select_related("student__user")
        .order_by("-submitted_at")
    )
    notifications = list(Notification.objects.filter(user=supervisor).order_by("-created_at")[:5])
    bookings = list(
        PresentationBooking.objects.filter(student__supervisor=supervisor, date__gte=now)
        .select_related("student__user")
        .order_by("date")
    )

    students_list = list(students_qs)
    submissions = list(submissions_qs)
    feedbacks = list(feedbacks_qs)
    reports = list(reports_qs)

    def initials_for_user(user):
        full_name = user.get_full_name().strip()
        if full_name:
            return "".join(part[0] for part in full_name.split()[:2]).upper()
        return user.username[:2].upper()

    def student_status(progress, last_active_dt):
        inactive_days = (today - last_active_dt.date()).days if last_active_dt else None
        if progress >= 75:
            return "On Track", "pill-green", "var(--green)", "Low"
        if inactive_days is not None and inactive_days >= 45:
            return "Stalled", "pill-red", "var(--red)", "High"
        if progress >= 40:
            return "At Risk", "pill-amber", "var(--amber)", "Medium"
        return "Stalled", "pill-red", "var(--red)", "High"

    def decision_meta(score):
        if score is None:
            return "Reviewed", "pill-gray", "var(--muted)"
        if score >= 80:
            return "Approved", "pill-green", "var(--green)"
        if score >= 65:
            return "Minor Revision", "pill-amber", "var(--amber)"
        return "Major Revision", "pill-red", "var(--red)"

    submissions_by_student = defaultdict(list)
    feedback_by_submission = {}
    for submission in submissions:
        cached_feedback = list(submission.feedback_set.all())
        feedback_by_submission[submission.id] = cached_feedback[0] if cached_feedback else None
        submissions_by_student[submission.student_id].append(submission)

    student_cards = []
    progress_distribution = {
        "on_track": 0,
        "needs_attention": 0,
        "at_risk": 0,
        "stalled": 0,
    }

    for student in students_list:
        milestones = list(student.milestone_set.all())
        student_submissions = submissions_by_student.get(student.id, [])
        last_submission = student_submissions[0] if student_submissions else None
        last_active = last_submission.submitted_at if last_submission else None

        total_milestones = len(milestones)
        completed_milestones = sum(1 for milestone in milestones if milestone.status == "done")
        progress = int(round((completed_milestones / total_milestones) * 100)) if total_milestones else 0

        status_label, status_badge, progress_color, risk_level = student_status(progress, last_active)
        if status_label == "On Track":
            progress_distribution["on_track"] += 1
        elif status_label == "At Risk":
            progress_distribution["at_risk"] += 1
        elif status_label == "Stalled":
            progress_distribution["stalled"] += 1
        else:
            progress_distribution["needs_attention"] += 1

        scores = [
            latest_feedback.score
            for latest_feedback in (feedback_by_submission.get(item.id) for item in student_submissions)
            if latest_feedback and latest_feedback.score is not None
        ]
        avg_score = round(sum(scores) / len(scores), 1) if scores else None

        recent_submissions = []
        for submission in student_submissions[:3]:
            latest_feedback = feedback_by_submission.get(submission.id)
            score = latest_feedback.score if latest_feedback else None
            decision_label, decision_class, _ = decision_meta(score)
            recent_submissions.append(
                {
                    "title": submission.title,
                    "status_label": "Under Review"
                    if submission.status in {"submitted", "pending"}
                    else decision_label,
                    "status_class": "pill-amber"
                    if submission.status in {"submitted", "pending"}
                    else decision_class,
                    "score": score,
                }
            )

        student_cards.append(
            {
                "student": student,
                "name": student.user.get_full_name() or student.user.username,
                "email": student.user.email,
                "programme": student.programme,
                "student_number": student.student_number,
                "profile_initials": initials_for_user(student.user),
                "progress": progress,
                "progress_color": progress_color,
                "status_label": status_label,
                "status_badge": status_badge,
                "risk_level": risk_level,
                "last_active": last_active,
                "avg_score": avg_score,
                "avg_score_display": f"{avg_score:.1f}%" if avg_score is not None else "-",
                "submission_count": len(student_submissions),
                "milestone_count": total_milestones,
                "recent_submissions": recent_submissions,
            }
        )

    total_students = len(student_cards)
    total_submissions = len(submissions)
    avg_progress = (
        int(round(sum(student["progress"] for student in student_cards) / total_students))
        if total_students
        else 0
    )

    pending_items = []
    reviewed_items = []
    all_items = []

    for submission in submissions:
        latest_feedback = feedback_by_submission.get(submission.id)
        has_feedback = latest_feedback is not None
        is_pending = submission.status in {"submitted", "pending"} or not has_feedback
        days_waiting = max((today - submission.submitted_at.date()).days, 0)

        if days_waiting >= 7:
            priority = "High"
            priority_badge = "pill-red"
            priority_dot_class = "prio-high"
            days_color = "var(--red)"
        elif days_waiting >= 4:
            priority = "Medium"
            priority_badge = "pill-orange"
            priority_dot_class = "prio-med"
            days_color = "var(--orange)"
        else:
            priority = "Low"
            priority_badge = "pill-blue"
            priority_dot_class = "prio-low"
            days_color = "var(--navy)"

        if submission.status in {"approved", "reviewed"}:
            status_pill = "pill-green"
        elif submission.status == "revision":
            status_pill = "pill-orange"
        elif submission.status in {"submitted", "pending"}:
            status_pill = "pill-amber"
        else:
            status_pill = "pill-gray"

        all_items.append(
            {
                "submission": submission,
                "feedback": latest_feedback,
                "feedback_score": (
                    f"{latest_feedback.score}%"
                    if latest_feedback and latest_feedback.score is not None
                    else "-"
                ),
                "status_pill": status_pill,
            }
        )

        if is_pending:
            pending_items.append(
                {
                    "submission": submission,
                    "student_name": submission.student.user.get_full_name()
                    or submission.student.user.username,
                    "programme": submission.student.programme,
                    "submitted_date": submission.submitted_at,
                    "days_waiting": days_waiting,
                    "days_color": days_color,
                    "priority": priority,
                    "priority_badge": priority_badge,
                    "priority_dot_class": priority_dot_class,
                }
            )
            continue

        score = latest_feedback.score if latest_feedback else None
        decision_label, decision_class, score_color = decision_meta(score)
        reviewed_items.append(
            {
                "submission": submission,
                "feedback": latest_feedback,
                "score": score,
                "score_display": f"{score}%" if score is not None else "-",
                "score_color": score_color,
                "decision_label": decision_label,
                "decision_class": decision_class,
                "reviewed_date": latest_feedback.created_at if latest_feedback else None,
            }
        )

    pending_reviews_count = len(pending_items)
    reviewed_this_month = sum(1 for feedback in feedbacks if feedback.created_at >= start_of_month)

    scored_feedback = [feedback for feedback in feedbacks if feedback.score is not None]
    avg_grade_awarded = (
        round(sum(feedback.score for feedback in scored_feedback) / len(scored_feedback), 1)
        if scored_feedback
        else 0
    )
    approved_count = sum(1 for feedback in scored_feedback if feedback.score >= 80)
    minor_revision_count = sum(1 for feedback in scored_feedback if 65 <= feedback.score < 80)
    major_revision_count = sum(1 for feedback in scored_feedback if feedback.score < 65)
    approval_rate = int(round((approved_count / len(scored_feedback)) * 100)) if scored_feedback else 0

    response_times = [
        (feedback.created_at - feedback.submission.submitted_at).total_seconds() / 86400
        for feedback in feedbacks
    ]
    avg_response_time = round(sum(response_times) / len(response_times), 1) if response_times else 0

    on_time_rate = (
        int(round(((total_submissions - pending_reviews_count) / total_submissions) * 100))
        if total_submissions
        else 0
    )

    trend_counts = defaultdict(int)
    for submission in submissions:
        trend_counts[(submission.submitted_at.year, submission.submitted_at.month)] += 1

    anchor_month = today.replace(day=1)
    trend_months = []
    for offset in range(5, -1, -1):
        month = anchor_month.month - offset
        year = anchor_month.year
        while month <= 0:
            month += 12
            year -= 1
        trend_months.append((year, month))

    max_trend_value = max((trend_counts[key] for key in trend_months), default=0)
    avg_trend_value = (
        sum(trend_counts[key] for key in trend_months) / len(trend_months) if trend_months else 0
    )
    submission_trends = []
    for year, month in trend_months:
        count = trend_counts[(year, month)]
        if max_trend_value and count == max_trend_value:
            color = "var(--green)"
        elif count > avg_trend_value:
            color = "var(--amber)"
        else:
            color = "var(--navy)"
        submission_trends.append(
            {
                "label": timezone.datetime(year, month, 1).strftime("%b"),
                "count": count,
                "height": int(round((count / max_trend_value) * 100)) if max_trend_value else 0,
                "color": color,
            }
        )

    total_distribution = sum(progress_distribution.values())
    circumference = 2 * math.pi * 54
    current_offset = 0
    progress_segments = []
    for key, color in (
        ("on_track", "#16A34A"),
        ("needs_attention", "#FFC107"),
        ("at_risk", "#EA580C"),
        ("stalled", "#DC2626"),
    ):
        value = progress_distribution[key]
        percent = int(round((value / total_distribution) * 100)) if total_distribution else 0
        arc_length = (value / total_distribution) * circumference if total_distribution else 0
        progress_segments.append(
            {
                "key": key,
                "color": color,
                "value": value,
                "percent": percent,
                "dasharray": f"{arc_length:.2f} {circumference:.2f}" if arc_length else f"0 {circumference:.2f}",
                "dashoffset": f"{-current_offset:.2f}",
            }
        )
        current_offset += arc_length

    schedule_start = today - timedelta(days=today.weekday())
    schedule_days = []
    for offset in range(5):
        day = schedule_start + timedelta(days=offset)
        day_bookings = [booking for booking in bookings if timezone.localtime(booking.date).date() == day]
        schedule_days.append({"date": day, "bookings": day_bookings, "is_today": day == today})

    meeting_rows = []
    for booking in bookings[:10]:
        if booking.status == "approved":
            status_badge = "pill-green"
            action_label = "Reschedule"
        elif booking.status == "pending":
            status_badge = "pill-amber"
            action_label = "Confirm"
        else:
            status_badge = "pill-red"
            action_label = "Review"
        meeting_rows.append(
            {
                "booking": booking,
                "status_badge": status_badge,
                "action_label": action_label,
            }
        )

    featured_review = pending_items[0] if pending_items else None
    featured_student = student_cards[0] if student_cards else None

    feedback_form = FeedbackForm()
    feedback_form.fields["submission"].queryset = submissions_qs
    feedback_form.fields["submission"].widget.attrs.update({"class": "form-control"})
    feedback_form.fields["comment"].widget.attrs.update({"class": "form-control", "rows": 5})

    context = {
        "supervisor": supervisor,
        "supervisor_initials": initials_for_user(supervisor),
        "students": student_cards,
        "submissions": submissions,
        "pending_reviews": pending_items,
        "reviewed_submissions": reviewed_items,
        "reviewed_items": reviewed_items,
        "all_items": all_items,
        "feedbacks": feedbacks,
        "reports": reports,
        "notifications": notifications,
        "bookings": bookings,
        "meeting_rows": meeting_rows,
        "schedule_days": schedule_days,
        "schedule_start": schedule_start,
        "submission_trends": submission_trends,
        "progress_distribution": progress_distribution,
        "progress_segments": progress_segments,
        "featured_review": featured_review,
        "featured_student": featured_student,
        "feedback_form": feedback_form,
        "report_stats": {
            "cohort_avg_progress": avg_progress,
            "on_time_rate": on_time_rate,
            "avg_grade_awarded": avg_grade_awarded,
            "students_at_risk": progress_distribution["at_risk"] + progress_distribution["stalled"],
            "total_feedback": len(feedbacks),
            "avg_response_time": avg_response_time,
            "approval_rate": approval_rate,
            "approved_pct": int(round((approved_count / len(scored_feedback)) * 100))
            if scored_feedback
            else 0,
            "minor_revision_pct": int(round((minor_revision_count / len(scored_feedback)) * 100))
            if scored_feedback
            else 0,
            "major_revision_pct": int(round((major_revision_count / len(scored_feedback)) * 100))
            if scored_feedback
            else 0,
        },
        "stats": {
            "total_students": total_students,
            "pending_reviews": pending_reviews_count,
            "reviewed_this_month": reviewed_this_month,
            "avg_progress": avg_progress,
            "total_submissions": total_submissions,
        },
    }

    return render(request, "supervisor/supervisor.html", context)


@login_required
@user_passes_test(lambda u: u.role in ["supervisor", "admin", "dean"])
def review_quarterly_report(request, pk):
    report = get_object_or_404(QuarterlyReport, pk=pk)
    if request.method == "POST":
        report.status = "reviewed"
        report.save()
        messages.success(request, "Report marked as reviewed.")
        return redirect("supervisor_dashboard")
    return render(request, "supervisor/review_report.html", {"report": report})
