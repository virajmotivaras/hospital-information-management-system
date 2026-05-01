import json

from django.contrib.auth.models import Group, User
from django.test import Client, TestCase

from repository.models import StaffProfile


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
            data=json.dumps({"full_name": "Patient", "department": "GENERAL"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_session_returns_hospital_profile(self):
        self.create_user("admin", "Admin")
        self.client.login(username="admin", password="test-pass")

        response = self.client.get("/api/session/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["hospital"]["name"], "Hospital Desk")

    def test_home_page_uses_post_logout_form(self):
        self.create_user("admin", "Admin")
        self.client.login(username="admin", password="test-pass")

        response = self.client.get("/")

        self.assertContains(response, 'action="/logout/"')
        self.assertContains(response, 'method="post"')

    def test_logout_post_redirects_to_login(self):
        self.create_user("admin", "Admin")
        self.client.login(username="admin", password="test-pass")

        response = self.client.post("/logout/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/login/")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_user_with_temporary_password_is_redirected_to_change_password(self):
        user = self.create_user("tempdoctor", "Doctor")
        StaffProfile.objects.create(user=user, must_change_password=True)

        response = self.client.post(
            "/login/",
            data={"username": "tempdoctor", "password": "test-pass"},
            follow=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/change-password/")

    def test_forced_password_change_clears_required_flag(self):
        user = self.create_user("tempadmin", "Admin")
        StaffProfile.objects.create(user=user, must_change_password=True)
        self.client.login(username="tempadmin", password="test-pass")

        response = self.client.post(
            "/change-password/",
            data={
                "current_password": "test-pass",
                "new_password": "NewPassword@123",
                "confirm_password": "NewPassword@123",
            },
        )

        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        self.assertTrue(user.check_password("NewPassword@123"))
        self.assertFalse(user.staff_profile.must_change_password)
