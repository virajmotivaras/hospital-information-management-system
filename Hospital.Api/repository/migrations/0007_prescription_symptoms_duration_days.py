from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("repository", "0006_appointment_duration"),
    ]

    operations = [
        migrations.RenameField(
            model_name="prescription",
            old_name="diagnosis",
            new_name="symptoms",
        ),
        migrations.AddField(
            model_name="prescription",
            name="symptoms_duration_days",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
