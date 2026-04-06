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