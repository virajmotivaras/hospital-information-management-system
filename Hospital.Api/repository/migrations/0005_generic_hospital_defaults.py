from django.db import migrations, models


def use_generic_defaults(apps, schema_editor):
    Appointment = apps.get_model("repository", "Appointment")
    Department = apps.get_model("repository", "Department")
    HospitalProfile = apps.get_model("repository", "HospitalProfile")
    Patient = apps.get_model("repository", "Patient")
    Visit = apps.get_model("repository", "Visit")

    general, _created = Department.objects.get_or_create(
        code="GENERAL",
        defaults={"name": "General", "display_order": 1, "is_active": True},
    )
    general.name = "General"
    general.is_active = True
    general.display_order = 1
    general.save()

    Patient.objects.filter(department="MATERNITY").update(department="GENERAL")
    Visit.objects.filter(department="MATERNITY").update(department="GENERAL")
    Appointment.objects.filter(department="MATERNITY").update(department="GENERAL")
    Department.objects.filter(code="MATERNITY").delete()
    HospitalProfile.objects.filter(tagline__in=["Maternity Hospital", "Gynecology and Pediatrics"]).update(tagline="Hospital")


class Migration(migrations.Migration):
    dependencies = [
        ("repository", "0004_departments_billing"),
    ]

    operations = [
        migrations.AlterField(
            model_name="hospitalprofile",
            name="tagline",
            field=models.CharField(default="Hospital", max_length=180),
        ),
        migrations.RunPython(use_generic_defaults, migrations.RunPython.noop),
    ]
