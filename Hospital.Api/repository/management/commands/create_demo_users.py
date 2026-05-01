from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from repository.models import StaffProfile


DEMO_USERS = {
    "reception": {
        "password": "Reception@123",
        "role": "Reception",
        "is_staff": False,
        "is_superuser": False,
    },
    "doctor": {
        "password": "Doctor@123",
        "role": "Doctor",
        "is_staff": False,
        "is_superuser": False,
    },
    "admin": {
        "password": "Admin@123",
        "role": "Admin",
        "is_staff": True,
        "is_superuser": True,
    },
}


class Command(BaseCommand):
    help = "Create or reset demo users for local prototype review."

    def handle(self, *args, **options):
        for username, config in DEMO_USERS.items():
            group, _ = Group.objects.get_or_create(name=config["role"])
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": f"{username}@hospital.local"},
            )
            user.set_password(config["password"])
            user.is_active = True
            user.is_staff = config["is_staff"]
            user.is_superuser = config["is_superuser"]
            user.save()
            user.groups.set([group])
            StaffProfile.objects.update_or_create(
                user=user,
                defaults={"must_change_password": True},
            )

            action = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(f"{action} {username} as {config['role']}")
            )
