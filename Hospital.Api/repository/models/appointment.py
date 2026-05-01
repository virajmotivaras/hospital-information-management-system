from django.db import models

from .patient import Patient


class Appointment(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        CHECKED_IN = "CHECKED_IN", "Checked in"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    department = models.CharField(max_length=20, choices=Patient.Department.choices)
    scheduled_for = models.DateTimeField()
    reason = models.CharField(max_length=240, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["scheduled_for"]
        indexes = [
            models.Index(fields=["scheduled_for", "status"]),
            models.Index(fields=["department", "scheduled_for"]),
        ]

    def __str__(self):
        return f"{self.patient.full_name} at {self.scheduled_for:%Y-%m-%d %H:%M}"
