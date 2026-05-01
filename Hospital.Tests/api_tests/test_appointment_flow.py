import json

from django.test import Client, TestCase
from django.contrib.auth.models import Group, User

from repository.models import Appointment, Patient


class AppointmentApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        Group.objects.get_or_create(name="Reception")
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
                    "department": "PEDIATRICS",
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
