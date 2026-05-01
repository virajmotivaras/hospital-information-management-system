from django.test import TestCase

from repository.models import HospitalProfile
from repository.repositories.settings_repository import get_hospital_profile


class SettingsRepositoryTests(TestCase):
    def test_hospital_profile_is_created_when_missing(self):
        profile = get_hospital_profile()

        self.assertEqual(profile.hospital_name, "Hospital Desk")
        self.assertEqual(HospitalProfile.objects.count(), 1)
