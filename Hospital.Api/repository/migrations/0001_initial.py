import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Patient",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=160)),
                ("phone_number", models.CharField(blank=True, max_length=32)),
                ("age_years", models.PositiveSmallIntegerField(blank=True, null=True)),
                (
                    "gender",
                    models.CharField(
                        choices=[
                            ("FEMALE", "Female"),
                            ("MALE", "Male"),
                            ("OTHER", "Other"),
                            ("NOT_SPECIFIED", "Not specified"),
                        ],
                        default="NOT_SPECIFIED",
                        max_length=20,
                    ),
                ),
                ("guardian_name", models.CharField(blank=True, max_length=160)),
                (
                    "department",
                    models.CharField(
                        choices=[("GYNECOLOGY", "Gynecology"), ("PEDIATRICS", "Pediatrics")],
                        max_length=20,
                    ),
                ),
                ("address", models.TextField(blank=True)),
                ("allergies", models.TextField(blank=True)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["full_name"],
                "indexes": [
                    models.Index(fields=["full_name"], name="repository_full_nam_1db5df_idx"),
                    models.Index(fields=["phone_number"], name="repository_phone_n_0a37e6_idx"),
                    models.Index(fields=["department"], name="repository_departm_f679a1_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Appointment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "department",
                    models.CharField(
                        choices=[("GYNECOLOGY", "Gynecology"), ("PEDIATRICS", "Pediatrics")],
                        max_length=20,
                    ),
                ),
                ("scheduled_for", models.DateTimeField()),
                ("reason", models.CharField(blank=True, max_length=240)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("SCHEDULED", "Scheduled"),
                            ("CHECKED_IN", "Checked in"),
                            ("COMPLETED", "Completed"),
                            ("CANCELLED", "Cancelled"),
                        ],
                        default="SCHEDULED",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "patient",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="appointments", to="repository.patient"),
                ),
            ],
            options={
                "ordering": ["scheduled_for"],
                "indexes": [
                    models.Index(fields=["scheduled_for", "status"], name="repository_schedule_12115d_idx"),
                    models.Index(fields=["department", "scheduled_for"], name="repository_departm_4e50d3_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Visit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("visit_type", models.CharField(choices=[("NEW", "New"), ("REPEAT", "Repeat")], max_length=20)),
                (
                    "department",
                    models.CharField(
                        choices=[("GYNECOLOGY", "Gynecology"), ("PEDIATRICS", "Pediatrics")],
                        max_length=20,
                    ),
                ),
                ("reason", models.CharField(blank=True, max_length=240)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("WAITING", "Waiting"),
                            ("IN_CONSULTATION", "In consultation"),
                            ("COMPLETED", "Completed"),
                            ("CANCELLED", "Cancelled"),
                        ],
                        default="WAITING",
                        max_length=24,
                    ),
                ),
                ("temperature_c", models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True)),
                ("weight_kg", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ("blood_pressure", models.CharField(blank=True, max_length=32)),
                ("check_in_time", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "patient",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="visits", to="repository.patient"),
                ),
            ],
            options={
                "ordering": ["-check_in_time"],
                "indexes": [
                    models.Index(fields=["status", "check_in_time"], name="repository_status_143778_idx"),
                    models.Index(fields=["department", "check_in_time"], name="repository_departm_d84eed_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Prescription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("doctor_name", models.CharField(max_length=120)),
                ("diagnosis", models.TextField(blank=True)),
                ("advice", models.TextField(blank=True)),
                ("follow_up_date", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "patient",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="prescriptions", to="repository.patient"),
                ),
                (
                    "visit",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="prescriptions",
                        to="repository.visit",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [models.Index(fields=["created_at"], name="repository_created_9c5a6d_idx")],
            },
        ),
        migrations.CreateModel(
            name="PrescriptionItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("medicine_name", models.CharField(max_length=160)),
                ("dosage", models.CharField(blank=True, max_length=80)),
                ("frequency", models.CharField(blank=True, max_length=80)),
                ("duration", models.CharField(blank=True, max_length=80)),
                ("instructions", models.CharField(blank=True, max_length=200)),
                (
                    "prescription",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="repository.prescription"),
                ),
            ],
            options={"ordering": ["id"]},
        ),
    ]
