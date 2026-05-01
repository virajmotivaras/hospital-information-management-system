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


def appointments_between(start, end):
    return list(
        Appointment.objects.select_related("patient")
        .filter(scheduled_for__gte=start, scheduled_for__lt=end)
        .exclude(status=Appointment.Status.CANCELLED)
        .order_by("scheduled_for")
    )


def upcoming_for_patient(patient_id):
    return list(
        Appointment.objects.select_related("patient")
        .filter(patient_id=patient_id, scheduled_for__gte=timezone.now())
        .exclude(status=Appointment.Status.CANCELLED)
        .order_by("scheduled_for")
    )


def past_for_patient(patient_id):
    return list(
        Appointment.objects.select_related("patient")
        .filter(patient_id=patient_id, scheduled_for__lt=timezone.now())
        .order_by("-scheduled_for")
    )
