from django.db import models


class Patient(models.Model):
    class Gender(models.TextChoices):
        FEMALE = "FEMALE", "Female"
        MALE = "MALE", "Male"
        OTHER = "OTHER", "Other"
        NOT_SPECIFIED = "NOT_SPECIFIED", "Not specified"

    full_name = models.CharField(max_length=160)
    phone_number = models.CharField(max_length=32, blank=True)
    age_years = models.PositiveSmallIntegerField(null=True, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        default=Gender.NOT_SPECIFIED,
    )
    guardian_name = models.CharField(max_length=160, blank=True)
    department = models.CharField(max_length=40)
    address = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]
        indexes = [
            models.Index(fields=["full_name"]),
            models.Index(fields=["phone_number"]),
            models.Index(fields=["department"]),
        ]

    def __str__(self):
        return self.full_name
