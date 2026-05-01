from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("repository", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="HospitalProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("hospital_name", models.CharField(default="Hospital Desk", max_length=180)),
                ("tagline", models.CharField(default="Gynecology and Pediatrics", max_length=180)),
                ("logo", models.FileField(blank=True, upload_to="hospital-logo/")),
                ("address", models.TextField(blank=True)),
                ("phone_number", models.CharField(blank=True, max_length=40)),
                (
                    "backup_folder_path",
                    models.CharField(
                        blank=True,
                        help_text="Use an empty local folder on the server machine for SQLite database backups.",
                        max_length=500,
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Hospital profile",
                "verbose_name_plural": "Hospital profile",
            },
        ),
        migrations.CreateModel(
            name="BackupRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("source_database", models.CharField(max_length=500)),
                ("backup_file", models.CharField(max_length=500)),
                ("created_by", models.CharField(blank=True, max_length=150)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
