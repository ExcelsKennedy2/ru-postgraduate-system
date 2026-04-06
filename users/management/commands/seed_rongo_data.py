from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from users.models import User
from students.models import Student
from pipeline.models import StudentProgress, Milestone, PipelineStage
from assessments.models import Submission, Feedback
from ai_module.models import Correction, CorrectionItem
from notifications.models import Notification
from erp_integration.models import FinanceRecord


class Command(BaseCommand):
    help = "Seed the database with Rongo University postgrad data"

    def handle(self, *args, **kwargs):
        self.stdout.write("🌱 Seeding Rongo University data...")

        # -----------------------------
        # 1. USERS
        # -----------------------------
        users_data = [
            {"username": f"student{i}", "role": "student", "unique_id": f"INF/{str(i+1).zfill(3)}/2022", 
             "email": f"student{i}@rongo.ac.ke"} for i in range(1, 12) if i != 3
        ] + [
            {"username": "supervisor1", "role": "supervisor", "unique_id": "STAFF/001", "email": "sup1@rongo.ac.ke"},
            {"username": "admin1", "role": "admin", "unique_id": "STAFF/ADMIN", "email": "admin@rongo.ac.ke"},
            {"username": "dean1", "role": "dean", "unique_id": "STAFF/DEAN", "email": "dean@rongo.ac.ke"},
        ]

        users = {}
        for data in users_data:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "role": data["role"],
                    "unique_id": data["unique_id"],
                    "email": data["email"],
                }
            )
            if created:
                user.set_password("password123")
                user.save()
                self.stdout.write(f"✅ Created user: {user.username}")
            users[data["username"]] = user

        # -----------------------------
        # 2. STUDENTS
        # -----------------------------
        students = {}
        for i in [1, 2] + list(range(4, 12)):
            username = f"student{i}"
            student, created = Student.objects.get_or_create(
                user=users[username],
                defaults={
                    "student_number": f"INF/{str(i).zfill(3)}/2022",
                    "programme": "Informatics",
                    "supervisor": users['supervisor1'],
                }
            )
            if created:
                self.stdout.write(f"🎓 Created student: {username}")
            students[username] = student

        # -----------------------------
        # 3. PIPELINE TEMPLATES
        # -----------------------------
        pipeline_templates = [
            [
                ("Concept Note", "in_progress"),
                ("Proposal Seminar", "upcoming"),
                ("Ethics/NACOSTI", "upcoming"),
                ("Data & Analysis", "upcoming"),
                ("Notice of Submission", "upcoming"),
                ("Thesis Exam", "upcoming"),
                ("Oral Defense", "upcoming"),
                ("Graduation", "upcoming"),
            ],
            [
                ("Concept Note", "done"),
                ("Proposal Seminar", "done"),
                ("Ethics/NACOSTI", "in_progress"),
                ("Data & Analysis", "upcoming"),
                ("Notice of Submission", "upcoming"),
                ("Thesis Exam", "upcoming"),
                ("Oral Defense", "upcoming"),
                ("Graduation", "upcoming"),
            ],
            [
                ("Concept Note", "done"),
                ("Proposal Seminar", "done"),
                ("Ethics/NACOSTI", "done"),
                ("Data & Analysis", "in_progress"),
                ("Notice of Submission", "upcoming"),
                ("Thesis Exam", "upcoming"),
                ("Oral Defense", "upcoming"),
                ("Graduation", "upcoming"),
            ],
            [
                ("Concept Note", "done"),
                ("Proposal Seminar", "done"),
                ("Ethics/NACOSTI", "done"),
                ("Data & Analysis", "done"),
                ("Notice of Submission", "done"),
                ("Thesis Exam", "in_progress"),
                ("Oral Defense", "upcoming"),
                ("Graduation", "upcoming"),
            ],
        ]

        stage_mapping = {
            "concept": PipelineStage.CONCEPT,
            "analysis": PipelineStage.DATA_COLLECTION,
            "methodology": PipelineStage.DATA_COLLECTION,
        }

        # -----------------------------
        # 4. SEED STUDENT DATA
        # -----------------------------
        for student in students.values():
            template = random.choice(pipeline_templates)

            # Student Progress
            StudentProgress.objects.get_or_create(
                student=student,
                defaults={"current_stage": random.choice(list(PipelineStage.values))},
            )

            # Milestones
            for title, status in template:
                Milestone.objects.get_or_create(
                    student=student,
                    title=title,
                    defaults={
                        "status": status,
                        "description": f"{title} milestone for {student.user.username}",
                        # "date": timezone.now().date() + timedelta(days=random.randint(3, 30)),
                    },
                )

            # Submissions + Feedback
            submission_types = ["concept", "analysis", "methodology"]
            for sub_type in random.sample(submission_types, k=2):
                submission, _ = Submission.objects.get_or_create(
                    student=student,
                    title=f"{sub_type.title()} Draft",
                    defaults={
                        "type": sub_type,
                        "chapter": "3" if sub_type == "analysis" else "",
                        "status": random.choice(["approved", "pending", "revision"]),
                        "stage": stage_mapping[sub_type],
                    },
                )
                Feedback.objects.get_or_create(
                    submission=submission,
                    defaults={
                        "comment": f"Feedback on {sub_type}. Improve clarity.",
                        "score": random.randint(60, 95),
                        "is_read": random.choice([True, False]),
                    },
                )

            # AI Corrections
            correction, _ = Correction.objects.get_or_create(
                student=student,
                defaults={"stage": PipelineStage.CONCEPT, "transcript": "AI suggestions generated."},
            )
            CorrectionItem.objects.get_or_create(
                correction=correction,
                defaults={
                    "text": random.choice([
                        "Improve introduction clarity.",
                        "Fix statistical interpretation.",
                        "Expand literature review.",
                    ]),
                    "severity": random.choice(["Minor", "Major"]),
                    "is_resolved": random.choice([True, False]),
                    "is_verified": False,
                },
            )

            # Finance Records (safe for duplicates)
            reference = f"FIN-2026-{student.id:03}"
            FinanceRecord.objects.get_or_create(
                student=student,
                reference=reference,
                defaults={
                    "status": random.choice(["approved", "pending", "rejected"]),
                    "comments": random.choice(["", "Balance pending", "Cleared", "Awaiting confirmation"]),
                },
            )

        # -----------------------------
        # 5. NOTIFICATIONS
        # -----------------------------
        for user in users.values():
            Notification.objects.get_or_create(
                user=user,
                defaults={"message": f"Welcome {user.username} to the Postgraduate System", "is_read": False},
            )

        self.stdout.write(self.style.SUCCESS("✅ Seeding completed successfully!"))

# students/management/commands/seed_bookings.py
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from students.models import Student, PresentationBooking

class Command(BaseCommand):
    help = "Seed PresentationBooking data for students"

    def handle(self, *args, **kwargs):
        students = Student.objects.all()
        if not students:
            self.stdout.write(self.style.ERROR("No students found!"))
            return

        titles = [
            "Chapter 1 Presentation",
            "Chapter 2 Presentation",
            "Chapter 3 Presentation",
            "Chapter 4 Presentation",
            "Final Research Presentation",
        ]

        for student in students:
            for title in random.sample(titles, k=3):  # 3 bookings per student
                # Generate a date at least 7 days in the future, random within 30 days
                future_days = random.randint(7, 30)
                booking_date = timezone.now() + timedelta(days=future_days, hours=random.randint(9, 17))

                # Random status
                status = random.choice(["pending", "approved", "rejected"])

                booking, created = PresentationBooking.objects.get_or_create(
                    student=student,
                    title=title,
                    date=booking_date,
                    defaults={"status": status}
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created booking: {booking}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Booking already exists: {booking}"))

        self.stdout.write(self.style.SUCCESS("Seeding PresentationBooking completed!"))