from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("repository", "0005_generic_hospital_defaults"),
    ]

    operations = [
        migrations.AddField(
            model_name="hospitalprofile",
            name="appointment_duration_minutes",
            field=models.PositiveSmallIntegerField(
                default=30,
                help_text="Default appointment slot length used to prevent overlapping bookings.",
            ),
        ),
    ]
