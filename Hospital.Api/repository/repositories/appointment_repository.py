from django.utils import timezone

from repository.models import Appointment


def create_appointment(patient, data):
    return Appointment.objects.create(
        patient=patient,
        department=data["department"],
        scheduled_for=data["scheduled_for"],
        reason=data.get("reason", ""),
    )


def upcoming_appointments(limit=40):
    return list(
        Appointment.objects.select_related("patient")
        .filter(status=Appointment.Status.SCHEDULED, scheduled_for__gte=timezone.now())
        .order_by("scheduled_for")[:limit]
    )
