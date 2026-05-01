from django.test import TestCase

from domain.common.errors import ValidationError
from domain.patients.rules import clean_patient_payload
from repository.models import Department


class PatientRulesTests(TestCase):
    def setUp(self):
        Department.objects.get_or_create(code="GENERAL", defaults={"name": "General"})

    def test_patient_name_is_required_for_check_in(self):
        with self.assertRaises(ValidationError):
            clean_patient_payload({"department": "GENERAL"})

    def test_department_defaults_to_first_configured_department(self):
        cleaned = clean_patient_payload({"full_name": "Anita"})

        self.assertEqual(cleaned["department"], "GENERAL")

    def test_invalid_age_is_rejected(self):
        with self.assertRaises(ValidationError):
            clean_patient_payload({"full_name": "Child", "age_years": "200"})
