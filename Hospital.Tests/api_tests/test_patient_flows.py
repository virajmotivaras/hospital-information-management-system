import json

from django.test import Client, TestCase
from django.contrib.auth.models import Group, User

from repository.models import Patient, Prescription, Visit


class PatientFlowApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        Group.objects.get_or_create(name="Reception")
        Group.objects.get_or_create(name="Doctor")
        self.reception = User.objects.create_user("reception", password="test-pass")
        self.reception.groups.add(Group.objects.get(name="Reception"))
        self.doctor = User.objects.create_user("doctor", password="test-pass")
        self.doctor.groups.add(Group.objects.get(name="Doctor"))
        self.client.login(username="reception", password="test-pass")

    def post_json(self, url, payload):
        return self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_new_patient_can_be_checked_in_with_minimum_details(self):
        response = self.post_json(
            "/api/visits/",
            {
                "full_name": "Anita Rao",
                "department": "GYNECOLOGY",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Patient.objects.count(), 1)
        self.assertEqual(Visit.objects.count(), 1)
        self.assertEqual(response.json()["visit"]["visit_type"], "NEW")

    def test_repeat_patient_is_detected_by_mobile_number(self):
        first = {
            "full_name": "Meera Shah",
            "phone_number": "98765 43210",
            "department": "PEDIATRICS",
            "guardian_name": "Raj Shah",
        }
        self.post_json("/api/visits/", first)

        response = self.post_json(
            "/api/visits/",
            {
                "full_name": "Meera Shah",
                "phone_number": "9876543210",
                "department": "PEDIATRICS",
                "reason": "Follow-up",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Patient.objects.count(), 1)
        self.assertEqual(Visit.objects.count(), 2)
        self.assertEqual(response.json()["visit"]["visit_type"], "REPEAT")

    def test_prescription_can_be_saved_and_printed(self):
        checkin = self.post_json(
            "/api/visits/",
            {
                "full_name": "Kavya Menon",
                "department": "GYNECOLOGY",
            },
        ).json()

        self.client.logout()
        self.client.login(username="doctor", password="test-pass")

        response = self.post_json(
            "/api/prescriptions/",
            {
                "patient_id": checkin["patient_id"],
                "visit_id": checkin["visit"]["id"],
                "doctor_name": "Iyer",
                "diagnosis": "Routine antenatal checkup",
                "advice": "Hydration and rest",
                "items": [
                    {
                        "medicine_name": "Folic Acid",
                        "dosage": "5 mg",
                        "frequency": "1-0-0",
                        "duration": "30 days",
                    }
                ],
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Prescription.objects.count(), 1)
        print_response = self.client.get(response.json()["print_url"])
        self.assertContains(print_response, "Folic Acid")
        self.assertContains(print_response, "Kavya Menon")
