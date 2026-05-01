from django.test import TestCase

from repository.models import Department, HospitalProfile
from repository.repositories.settings_repository import active_departments, get_hospital_profile


class SettingsRepositoryTests(TestCase):
    def test_hospital_profile_is_created_when_missing(self):
        profile = get_hospital_profile()

        self.assertEqual(profile.hospital_name, "Hospital Desk")
        self.assertEqual(HospitalProfile.objects.count(), 1)

    def test_default_department_is_created_when_missing(self):
        departments = active_departments()

        self.assertEqual(departments[0].code, "GENERAL")
        self.assertEqual(Department.objects.count(), 1)
