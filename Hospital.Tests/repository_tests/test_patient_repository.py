from django.test import TestCase

from repository.repositories import patient_repository


class PatientRepositoryTests(TestCase):
    def test_phone_number_is_normalized_before_matching(self):
        patient_repository.create_patient(
            {
                "full_name": "Asha Kumar",
                "phone_number": "98 76-54",
                "department": "GENERAL",
            }
        )

        patient = patient_repository.find_existing_patient(
            full_name="Asha Kumar",
            phone_number="987654",
        )

        self.assertIsNotNone(patient)
        self.assertEqual(patient.full_name, "Asha Kumar")
