from django.test import SimpleTestCase

from domain.common.errors import ValidationError
from domain.patients.rules import clean_patient_payload


class PatientRulesTests(SimpleTestCase):
    def test_patient_name_is_required_for_check_in(self):
        with self.assertRaises(ValidationError):
            clean_patient_payload({"department": "GYNECOLOGY"})

    def test_department_defaults_to_gynecology(self):
        cleaned = clean_patient_payload({"full_name": "Anita"})

        self.assertEqual(cleaned["department"], "GYNECOLOGY")

    def test_invalid_age_is_rejected(self):
        with self.assertRaises(ValidationError):
            clean_patient_payload({"full_name": "Child", "age_years": "200"})
