from django.db import models

from .patient import Patient
from .visit import Visit


class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="prescriptions")
    visit = models.ForeignKey(Visit, on_delete=models.SET_NULL, null=True, blank=True, related_name="prescriptions")
    doctor_name = models.CharField(max_length=120)
    diagnosis = models.TextField(blank=True)
    advice = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["created_at"])]

    def __str__(self):
        return f"Prescription for {self.patient.full_name}"


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="items")
    medicine_name = models.CharField(max_length=160)
    dosage = models.CharField(max_length=80, blank=True)
    frequency = models.CharField(max_length=80, blank=True)
    duration = models.CharField(max_length=80, blank=True)
    instructions = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.medicine_name
