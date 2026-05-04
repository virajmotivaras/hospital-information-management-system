from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("repository", "0007_prescription_symptoms_duration_days"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="prescription",
            name="symptoms_duration_days",
        ),
        migrations.AddField(
            model_name="prescription",
            name="symptom_entries",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="prescription",
            name="diagnosis",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="prescription",
            name="examination_findings",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="hospitalprofile",
            name="include_prescription_print_header",
            field=models.BooleanField(
                default=False,
                help_text="Show hospital name, logo, address, and phone number on printed prescriptions.",
            ),
        ),
    ]
