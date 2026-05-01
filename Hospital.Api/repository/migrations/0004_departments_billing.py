from decimal import Decimal

import django.db.models.deletion
from django.db import migrations, models


def seed_default_department(apps, schema_editor):
    Department = apps.get_model("repository", "Department")
    HospitalProfile = apps.get_model("repository", "HospitalProfile")
    Department.objects.get_or_create(
        code="MATERNITY",
        defaults={"name": "Maternity", "display_order": 1, "is_active": True},
    )
    HospitalProfile.objects.filter(tagline="Gynecology and Pediatrics").update(tagline="Maternity Hospital")


class Migration(migrations.Migration):
    dependencies = [
        ("repository", "0003_staffprofile"),
    ]

    operations = [
        migrations.CreateModel(
            name="Department",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=40, unique=True)),
                ("name", models.CharField(max_length=120)),
                ("is_active", models.BooleanField(default=True)),
                ("display_order", models.PositiveSmallIntegerField(default=0)),
            ],
            options={"ordering": ["display_order", "name"]},
        ),
        migrations.AlterField(
            model_name="appointment",
            name="department",
            field=models.CharField(max_length=40),
        ),
        migrations.AlterField(
            model_name="patient",
            name="department",
            field=models.CharField(max_length=40),
        ),
        migrations.AlterField(
            model_name="visit",
            name="department",
            field=models.CharField(max_length=40),
        ),
        migrations.AlterField(
            model_name="hospitalprofile",
            name="tagline",
            field=models.CharField(default="Maternity Hospital", max_length=180),
        ),
        migrations.CreateModel(
            name="Bill",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("DRAFT", "Draft"),
                            ("UNPAID", "Unpaid"),
                            ("PARTIALLY_PAID", "Partially paid"),
                            ("PAID", "Paid"),
                            ("CANCELLED", "Cancelled"),
                        ],
                        default="UNPAID",
                        max_length=24,
                    ),
                ),
                ("paid_amount", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "patient",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bills", to="repository.patient"),
                ),
                (
                    "visit",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="bills",
                        to="repository.visit",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["patient", "created_at"], name="repository_patient_43dfba_idx"),
                    models.Index(fields=["status", "created_at"], name="repository_status_5fe3e2_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="BillLineItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("description", models.CharField(max_length=180)),
                ("quantity", models.DecimalField(decimal_places=2, default=Decimal("1.00"), max_digits=8)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "bill",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="repository.bill"),
                ),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.RunPython(seed_default_department, migrations.RunPython.noop),
    ]
