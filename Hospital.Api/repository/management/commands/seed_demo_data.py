from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from repository.models import Appointment, Bill, BillLineItem, Department, Patient, Prescription, PrescriptionItem, Visit
from repository.repositories.settings_repository import ensure_default_department


class Command(BaseCommand):
    help = "Seed clickable demo patients, appointments, prescriptions, visits, and bills."

    def handle(self, *args, **options):
        department = ensure_default_department()
        Department.objects.filter(code=department.code).update(is_active=True)

        patients = [
            {
                "full_name": "Anita Rao",
                "phone_number": "9000010001",
                "age_years": 29,
                "gender": Patient.Gender.FEMALE,
                "guardian_name": "Vikram Rao",
                "reason": "Routine consultation",
                "symptoms": "General follow-up",
                "medicine": "Iron Supplement",
                "bill_item": "Consultation",
                "bill_total": "500.00",
                "paid": "500.00",
            },
            {
                "full_name": "Meera Shah",
                "phone_number": "9000010002",
                "age_years": 34,
                "gender": Patient.Gender.FEMALE,
                "guardian_name": "Raj Shah",
                "reason": "Follow-up visit",
                "symptoms": "Review after previous visit",
                "medicine": "Calcium Tablets",
                "bill_item": "Consultation and scan",
                "bill_total": "1500.00",
                "paid": "1000.00",
            },
            {
                "full_name": "Kavya Menon",
                "phone_number": "9000010003",
                "age_years": 26,
                "gender": Patient.Gender.FEMALE,
                "guardian_name": "Arjun Menon",
                "reason": "New patient check-in",
                "symptoms": "Initial assessment",
                "medicine": "Folic Acid",
                "bill_item": "Registration and consultation",
                "bill_total": "700.00",
                "paid": "0.00",
            },
            {
                "full_name": "Sara Khan",
                "phone_number": "9000010004",
                "age_years": 31,
                "gender": Patient.Gender.FEMALE,
                "guardian_name": "Imran Khan",
                "reason": "Scheduled review",
                "symptoms": "Stable, continue advice",
                "medicine": "Vitamin D",
                "bill_item": "Consultation",
                "bill_total": "500.00",
                "paid": "250.00",
            },
        ]

        for index, item in enumerate(patients):
            patient, _created = Patient.objects.update_or_create(
                phone_number=item["phone_number"],
                defaults={
                    "full_name": item["full_name"],
                    "age_years": item["age_years"],
                    "gender": item["gender"],
                    "guardian_name": item["guardian_name"],
                    "department": department.code,
                    "allergies": "None known" if index % 2 == 0 else "",
                    "notes": "Demo patient record",
                },
            )

            Visit.objects.get_or_create(
                patient=patient,
                status=Visit.Status.WAITING if index < 2 else Visit.Status.COMPLETED,
                defaults={
                    "visit_type": Visit.VisitType.REPEAT if index % 2 else Visit.VisitType.NEW,
                    "department": department.code,
                    "reason": item["reason"],
                    "temperature_c": Decimal("36.8") + Decimal(index) / Decimal("10"),
                    "weight_kg": Decimal("58.00") + Decimal(index),
                    "blood_pressure": "120/80",
                },
            )

            Appointment.objects.get_or_create(
                patient=patient,
                scheduled_for=timezone.now() - timezone.timedelta(days=30 + index),
                defaults={
                    "department": department.code,
                    "reason": "Past review",
                    "status": Appointment.Status.COMPLETED,
                },
            )
            Appointment.objects.get_or_create(
                patient=patient,
                scheduled_for=timezone.now() + timezone.timedelta(days=7 + index),
                defaults={
                    "department": department.code,
                    "reason": "Upcoming review",
                    "status": Appointment.Status.SCHEDULED,
                },
            )

            prescription, _created = Prescription.objects.get_or_create(
                patient=patient,
                doctor_name="Dr. Demo",
                symptoms=item["symptoms"],
                defaults={
                    "symptom_entries": [{"symptom": item["symptoms"], "days": 3 + index}],
                    "diagnosis": "Demo diagnosis pending review",
                    "examination_findings": "General condition stable.",
                    "advice": "Drink water, rest, and return if symptoms increase.",
                    "follow_up_date": timezone.localdate() + timezone.timedelta(days=14),
                },
            )
            PrescriptionItem.objects.get_or_create(
                prescription=prescription,
                medicine_name=item["medicine"],
                defaults={
                    "dosage": "1 tablet",
                    "frequency": "1-0-1",
                    "duration": "10 days",
                    "instructions": "After food",
                },
            )

            bill, _created = Bill.objects.get_or_create(
                patient=patient,
                notes="Demo bill",
                defaults={"paid_amount": Decimal(item["paid"])},
            )
            BillLineItem.objects.get_or_create(
                bill=bill,
                description=item["bill_item"],
                defaults={
                    "quantity": Decimal("1.00"),
                    "unit_price": Decimal(item["bill_total"]),
                },
            )
            bill.refresh_status_from_amounts()
            bill.save(update_fields=["status", "updated_at"])

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(patients)} demo patients."))
