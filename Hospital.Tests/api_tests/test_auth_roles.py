import json

from django.contrib.auth.models import Group, User
from django.test import Client, TestCase


class AuthRoleTests(TestCase):
    def setUp(self):
        self.client = Client()
        for role in ["Reception", "Doctor", "Admin"]:
            Group.objects.get_or_create(name=role)

    def create_user(self, username, role):
        user = User.objects.create_user(username, password="test-pass")
        user.groups.add(Group.objects.get(name=role))
        return user

    def test_anonymous_api_request_requires_login(self):
        response = self.client.get("/api/session/")

        self.assertEqual(response.status_code, 401)

    def test_reception_cannot_write_prescription(self):
        self.create_user("reception", "Reception")
        self.client.login(username="reception", password="test-pass")

        response = self.client.post(
            "/api/prescriptions/",
            data=json.dumps({"doctor_name": "Doctor", "items": []}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_doctor_cannot_check_in_patient(self):
        self.create_user("doctor", "Doctor")
        self.client.login(username="doctor", password="test-pass")

        response = self.client.post(
            "/api/visits/",
            data=json.dumps({"full_name": "Patient", "department": "GYNECOLOGY"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_session_returns_hospital_profile(self):
        self.create_user("admin", "Admin")
        self.client.login(username="admin", password="test-pass")

        response = self.client.get("/api/session/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["hospital"]["name"], "Hospital Desk")
