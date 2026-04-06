from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Count

from assessments.models import Submission, Feedback
from assessments.forms import FeedbackForm
from students.models import Student, QuarterlyReport, PresentationBooking
from notifications.models import Notification

@login_required
@user_passes_test(lambda u: u.is_staff)
def supervisor_dashboard(request):
    supervisor = request.user

    students = Student.objects.filter(supervisor=supervisor).select_related('user')
    submissions = Submission.objects.filter(student__supervisor=supervisor).select_related('student__user').order_by('-submitted_at')
    pending_reviews = submissions.filter(status='submitted')
    reviewed_submissions = submissions.filter(status='reviewed')
    feedbacks = Feedback.objects.filter(supervisor=supervisor).select_related('submission__student__user').order_by('-created_at')
    reports = QuarterlyReport.objects.filter(student__supervisor=supervisor).select_related('student__user').order_by('-submitted_at')
    notifications = Notification.objects.filter(user=supervisor).order_by('-created_at')[:6]
    bookings = PresentationBooking.objects.filter(student__supervisor=supervisor, date__gte=timezone.now()).select_related('student__user').order_by('date')

    total_students = students.count()
    total_submissions = submissions.count()
    pending_reviews_count = pending_reviews.count()
    reviewed_this_month = feedbacks.filter(
        created_at__year=timezone.now().year,
        created_at__month=timezone.now().month,
    ).count()
    avg_progress = int((reviewed_submissions.count() / total_submissions) * 100) if total_submissions else 0
    avg_grade_awarded = round(feedbacks.aggregate(avg_score=Avg('score'))['avg_score'] or 0, 1)
    on_time_rate = int(((total_submissions - pending_reviews_count) / total_submissions) * 100) if total_submissions else 0

    student_cards = []
    for student in students.prefetch_related('submission_set'):
        student_submissions = list(student.submission_set.all())
        reviewed = len([sub for sub in student_submissions if sub.status == 'reviewed'])
        total = len(student_submissions)
        progress = int((reviewed / total) * 100) if total else 0
        if progress >= 80:
            status_label = 'On Track'
            badge = 'pill-green'
            risk = 'Low'
            progress_color = 'var(--green)'
        elif progress >= 50:
            status_label = 'Needs Attention'
            badge = 'pill-amber'
            risk = 'Medium'
            progress_color = 'var(--amber)'
        else:
            status_label = 'At Risk'
            badge = 'pill-red'
            risk = 'High'
            progress_color = 'var(--red)'

        last_submission = max(student_submissions, key=lambda s: s.submitted_at, default=None)
        last_active = last_submission.submitted_at if last_submission else None

        student_cards.append({
            'student': student,
            'profile_initials': ''.join([part[0] for part in student.user.get_full_name().split()][:2]).upper(),
            'programme': student.programme,
            'email': student.user.email,
            'student_number': student.student_number,
            'progress': progress,
            'progress_color': progress_color,
            'status_label': status_label,
            'status_badge': badge,
            'risk_level': risk,
            'last_active': last_active,
            'avg_score': None,
            'submission_count': total,
        })

    progress_distribution = {
        'on_track': sum(1 for student in student_cards if student['risk_level'] == 'Low'),
        'needs_attention': sum(1 for student in student_cards if student['risk_level'] == 'Medium'),
        'at_risk': sum(1 for student in student_cards if student['risk_level'] == 'High'),
        'stalled': 0,
    }

    pending_items = []
    for submission in pending_reviews:
        days_waiting = (timezone.now() - submission.submitted_at).days
        if days_waiting >= 7:
            priority = 'High'
            badge = 'pill-red'
            days_color = 'var(--red)'
            dot_class = 'prio-high'
        elif days_waiting >= 4:
            priority = 'Medium'
            badge = 'pill-orange'
            days_color = 'var(--orange)'
            dot_class = 'prio-med'
        else:
            priority = 'Low'
            badge = 'pill-blue'
            days_color = 'var(--navy)'
            dot_class = 'prio-low'

        pending_items.append({
            'submission': submission,
            'student_name': submission.student.user.get_full_name(),
            'programme': submission.student.programme,
            'days_waiting': days_waiting,
            'priority': priority,
            'priority_badge': badge,
            'priority_dot_class': dot_class,
            'days_color': days_color,
            'submitted_date': submission.submitted_at,
        })

    recent_submissions = submissions[:5]
    recent_feedback = feedbacks[:5]

    reviewed_items = []
    for submission in reviewed_submissions:
        latest_feedback = submission.feedback_set.order_by('-created_at').first()
        score = latest_feedback.score if latest_feedback else None
        if score is not None:
            if score >= 80:
                decision_label = 'Approved'
                decision_class = 'pill-green'
                score_color = 'var(--green)'
            elif score >= 65:
                decision_label = 'Minor Revision'
                decision_class = 'pill-amber'
                score_color = 'var(--amber)'
            else:
                decision_label = 'Major Revision'
                decision_class = 'pill-red'
                score_color = 'var(--red)'
        else:
            decision_label = 'Reviewed'
            decision_class = 'pill-gray'
            score_color = 'var(--muted)'

        reviewed_items.append({
            'submission': submission,
            'score': score,
            'score_display': f"{score}%" if score is not None else '—',
            'score_color': score_color,
            'decision_label': decision_label,
            'decision_class': decision_class,
            'reviewed_date': latest_feedback.created_at if latest_feedback else None,
        })

    all_items = []
    for submission in submissions:
        latest_feedback = submission.feedback_set.order_by('-created_at').first()
        if submission.status in ['approved', 'reviewed']:
            status_pill = 'pill-green'
        elif submission.status in ['revision']:
            status_pill = 'pill-orange'
        elif submission.status in ['submitted', 'pending']:
            status_pill = 'pill-amber'
        else:
            status_pill = 'pill-gray'

        all_items.append({
            'submission': submission,
            'feedback_score': f"{latest_feedback.score}%" if latest_feedback and latest_feedback.score is not None else '—',
            'status_pill': status_pill,
        })

    feedback_form = FeedbackForm()
    feedback_form.fields['submission'].queryset = submissions

    activity_feed = []
    for submission in recent_submissions:
        activity_feed.append({
            'title': f"{submission.student.user.get_full_name()} submitted {submission.title}",
            'time': submission.submitted_at,
            'type': 'submission',
        })
    for feedback in recent_feedback:
        activity_feed.append({
            'title': f"Feedback given for {feedback.submission.title}",
            'time': feedback.created_at,
            'type': 'feedback',
        })
    activity_feed.sort(key=lambda item: item['time'], reverse=True)

    supervisor_initials = ''.join([part[0] for part in supervisor.get_full_name().split()][:2]).upper() if supervisor.get_full_name() else supervisor.username[:2].upper()

    context = {
        'supervisor': supervisor,
        'supervisor_initials': supervisor_initials,
        'students': student_cards,
        'submissions': submissions,
        'pending_reviews': pending_items,
        'reviewed_submissions': reviewed_submissions,
        'feedbacks': feedbacks,
        'reports': reports,
        'notifications': notifications,
        'stats': {
            'total_students': total_students,
            'pending_reviews': pending_reviews_count,
            'reviewed_this_month': reviewed_this_month,
            'avg_progress': avg_progress,
            'total_submissions': total_submissions,
        },
        'progress_distribution': progress_distribution,
        'feedback_form': feedback_form,
        'reviewed_items': reviewed_items,
        'all_items': all_items,
        'bookings': bookings,
        'activity_feed': activity_feed[:6],
    }

    return render(request, 'supervisor/supervisor.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def review_quarterly_report(request, pk):
    report = get_object_or_404(QuarterlyReport, pk=pk)
    if request.method == 'POST':
        report.status = 'reviewed'
        report.save()
        messages.success(request, 'Report marked as reviewed.')
        return redirect('supervisor_dashboard')
    return render(request, 'supervisor/review_report.html', {'report': report})