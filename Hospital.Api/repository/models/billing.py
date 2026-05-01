from decimal import Decimal

from django.db import models

from .patient import Patient
from .visit import Visit


class Bill(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        UNPAID = "UNPAID", "Unpaid"
        PARTIALLY_PAID = "PARTIALLY_PAID", "Partially paid"
        PAID = "PAID", "Paid"
        CANCELLED = "CANCELLED", "Cancelled"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="bills")
    visit = models.ForeignKey(Visit, on_delete=models.SET_NULL, null=True, blank=True, related_name="bills")
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.UNPAID)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["patient", "created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]

    @property
    def total_amount(self):
        return sum((item.line_total for item in self.items.all()), Decimal("0.00"))

    @property
    def due_amount(self):
        due = self.total_amount - self.paid_amount
        return max(due, Decimal("0.00"))

    def refresh_status_from_amounts(self):
        if self.status == self.Status.CANCELLED:
            return
        total = self.total_amount
        if total <= 0:
            self.status = self.Status.DRAFT
        elif self.paid_amount <= 0:
            self.status = self.Status.UNPAID
        elif self.paid_amount < total:
            self.status = self.Status.PARTIALLY_PAID
        else:
            self.status = self.Status.PAID

    def __str__(self):
        return f"Bill #{self.id} - {self.patient.full_name}"


class BillLineItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name="items")
    description = models.CharField(max_length=180)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("1.00"))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["id"]

    @property
    def line_total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return self.description
