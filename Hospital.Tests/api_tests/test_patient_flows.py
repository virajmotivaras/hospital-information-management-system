import json
from datetime import timedelta

from django.test import Client, TestCase
from django.contrib.auth.models import Group, User
from django.utils import timezone

from repository.models import Appointment, Bill, Department, Patient, Prescription, Visit


class PatientFlowApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        Group.objects.get_or_create(name="Reception")
        Group.objects.get_or_create(name="Doctor")
        Group.objects.get_or_create(name="Admin")
        Department.objects.get_or_create(code="GENERAL", defaults={"name": "General"})
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
                "department": "GENERAL",
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
            "department": "GENERAL",
            "guardian_name": "Raj Shah",
        }
        self.post_json("/api/visits/", first)

        response = self.post_json(
            "/api/visits/",
            {
                "full_name": "Meera Shah",
                "phone_number": "9876543210",
                "department": "GENERAL",
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
                "department": "GENERAL",
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
                "symptom_entries": [
                    {"symptom": "R50.9 - Fever, unspecified", "days": 2},
                    {"symptom": "R05.9 - Cough, unspecified", "days": 3},
                ],
                "diagnosis": "Viral upper respiratory infection",
                "examination_findings": "Throat congestion present.",
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
        prescription_payload = response.json()["prescription"]
        self.assertEqual(len(prescription_payload["symptom_entries"]), 2)
        self.assertEqual(prescription_payload["diagnosis"], "Viral upper respiratory infection")
        self.assertEqual(prescription_payload["examination_findings"], "Throat congestion present.")
        print_response = self.client.get(response.json()["print_url"])
        self.assertContains(print_response, "Folic Acid")
        self.assertContains(print_response, "Kavya Menon")
        self.assertContains(print_response, "R50.9 - Fever, unspecified")
        self.assertContains(print_response, "2 days")
        self.assertContains(print_response, "R05.9 - Cough, unspecified")
        self.assertContains(print_response, "3 days")
        self.assertContains(print_response, "Viral upper respiratory infection")
        self.assertContains(print_response, "Throat congestion present.")

    def test_doctor_can_view_patient_appointment_and_prescription_history(self):
        patient = Patient.objects.create(full_name="Sara Khan", department="GENERAL")
        Appointment.objects.create(
            patient=patient,
            department="GENERAL",
            scheduled_for=timezone.now() - timedelta(days=10),
            reason="Previous visit",
        )
        Appointment.objects.create(
            patient=patient,
            department="GENERAL",
            scheduled_for=timezone.now() + timedelta(days=5),
            reason="Next visit",
        )
        prescription = Prescription.objects.create(patient=patient, doctor_name="Doctor", symptoms="Follow-up")

        self.client.logout()
        self.client.login(username="doctor", password="test-pass")
        response = self.client.get(f"/api/patients/{patient.id}/history/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload["appointments"]["past"]), 1)
        self.assertEqual(len(payload["appointments"]["upcoming"]), 1)
        self.assertEqual(payload["prescriptions"][0]["id"], prescription.id)
        self.assertEqual(payload["bills"], [])

    def test_reception_can_create_and_view_patient_bill_history(self):
        patient = Patient.objects.create(full_name="Billing Patient", department="GENERAL")

        response = self.post_json(
            f"/api/patients/{patient.id}/bills/",
            {
                "paid_amount": "200.00",
                "items": [
                    {
                        "description": "Consultation",
                        "quantity": "1",
                        "unit_price": "500.00",
                    }
                ],
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Bill.objects.count(), 1)
        self.assertEqual(response.json()["bill"]["status"], "PARTIALLY_PAID")

        history = self.client.get(f"/api/patients/{patient.id}/history/")
        self.assertEqual(history.status_code, 200)
        self.assertEqual(history.json()["bills"][0]["due_amount"], "300.00")
