import json
from datetime import timedelta

from django.test import Client, TestCase
from django.contrib.auth.models import Group, User
from django.utils import timezone

from repository.models import Appointment, Department, Patient


class AppointmentApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        Group.objects.get_or_create(name="Reception")
        Group.objects.get_or_create(name="Doctor")
        Department.objects.get_or_create(code="GENERAL", defaults={"name": "General"})
        user = User.objects.create_user("reception", password="test-pass")
        user.groups.add(Group.objects.get(name="Reception"))
        self.client.login(username="reception", password="test-pass")

    def test_appointment_creates_patient_when_needed(self):
        response = self.client.post(
            "/api/appointments/",
            data=json.dumps(
                {
                    "full_name": "Neha Patel",
                    "phone_number": "9000011111",
                    "department": "GENERAL",
                    "guardian_name": "Amit Patel",
                    "scheduled_for": "2026-05-02T10:30:00+02:00",
                    "reason": "Vaccination",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Patient.objects.count(), 1)
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertEqual(response.json()["appointment"]["patient"]["full_name"], "Neha Patel")

    def test_doctor_can_view_week_appointments_but_not_create_them(self):
        doctor = User.objects.create_user("doctor", password="test-pass")
        doctor.groups.add(Group.objects.get(name="Doctor"))
        patient = Patient.objects.create(full_name="Calendar Patient", department="GENERAL")
        week_start = timezone.now()
        Appointment.objects.create(
            patient=patient,
            department="GENERAL",
            scheduled_for=week_start + timedelta(days=1),
            reason="Follow-up",
        )
        Appointment.objects.create(
            patient=patient,
            department="GENERAL",
            scheduled_for=week_start + timedelta(days=9),
            reason="Outside visible week",
        )

        self.client.logout()
        self.client.login(username="doctor", password="test-pass")

        response = self.client.get(
            "/api/appointments/",
            {
                "start": week_start.isoformat(),
                "end": (week_start + timedelta(days=7)).isoformat(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["appointments"]), 1)
        self.assertEqual(response.json()["appointments"][0]["reason"], "Follow-up")

        create_response = self.client.post(
            "/api/appointments/",
            data=json.dumps(
                {
                    "full_name": "Blocked Create",
                    "department": "GENERAL",
                    "scheduled_for": (week_start + timedelta(days=2)).isoformat(),
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, 403)
