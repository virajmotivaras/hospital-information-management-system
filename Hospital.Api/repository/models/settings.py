from django.core.exceptions import ValidationError
from django.db import models


class HospitalProfile(models.Model):
    hospital_name = models.CharField(max_length=180, default="Hospital Desk")
    tagline = models.CharField(max_length=180, default="Gynecology and Pediatrics")
    logo = models.FileField(upload_to="hospital-logo/", blank=True)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=40, blank=True)
    backup_folder_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Use an empty local folder on the server machine for SQLite database backups.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Hospital profile"
        verbose_name_plural = "Hospital profile"

    def clean(self):
        super().clean()
        if self.backup_folder_path:
            from pathlib import Path

            path = Path(self.backup_folder_path)
            if not path.exists():
                raise ValidationError({"backup_folder_path": "This folder does not exist on the server."})
            if not path.is_dir():
                raise ValidationError({"backup_folder_path": "This path must be a folder."})

    def __str__(self):
        return self.hospital_name


class BackupRecord(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    source_database = models.CharField(max_length=500)
    backup_file = models.CharField(max_length=500)
    created_by = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.backup_file
