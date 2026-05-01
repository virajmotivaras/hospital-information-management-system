from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from domain.common.roles import ALL_ROLES
from repository.repositories.settings_repository import ensure_default_department, get_hospital_profile


class Command(BaseCommand):
    help = "Create default hospital roles and the default hospital profile."

    def handle(self, *args, **options):
        for role in ALL_ROLES:
            Group.objects.get_or_create(name=role)
            self.stdout.write(self.style.SUCCESS(f"Role ready: {role}"))

        profile = get_hospital_profile()
        self.stdout.write(self.style.SUCCESS(f"Hospital profile ready: {profile.hospital_name}"))
        department = ensure_default_department()
        self.stdout.write(self.style.SUCCESS(f"Department ready: {department.name}"))
