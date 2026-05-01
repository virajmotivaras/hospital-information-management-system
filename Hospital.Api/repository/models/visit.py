from django.db import models

from .patient import Patient


class Visit(models.Model):
    class VisitType(models.TextChoices):
        NEW = "NEW", "New"
        REPEAT = "REPEAT", "Repeat"

    class Status(models.TextChoices):
        WAITING = "WAITING", "Waiting"
        IN_CONSULTATION = "IN_CONSULTATION", "In consultation"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="visits")
    visit_type = models.CharField(max_length=20, choices=VisitType.choices)
    department = models.CharField(max_length=40)
    reason = models.CharField(max_length=240, blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.WAITING)
    temperature_c = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    blood_pressure = models.CharField(max_length=32, blank=True)
    check_in_time = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-check_in_time"]
        indexes = [
            models.Index(fields=["status", "check_in_time"]),
            models.Index(fields=["department", "check_in_time"]),
        ]

    def __str__(self):
        return f"{self.patient.full_name} - {self.get_status_display()}"
