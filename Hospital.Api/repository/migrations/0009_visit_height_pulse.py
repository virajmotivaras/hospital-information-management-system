from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("repository", "0008_prescription_structured_symptoms_print_header"),
    ]

    operations = [
        migrations.AddField(
            model_name="visit",
            name="height_cm",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name="visit",
            name="pulse_bpm",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
