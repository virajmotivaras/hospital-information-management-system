from django.conf import settings
from django.db import models


class StaffProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="staff_profile")
    must_change_password = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
