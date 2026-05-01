from django.utils import timezone
from django.utils.dateparse import parse_datetime

from domain.common.errors import ValidationError
from domain.patients.services import register_or_update_patient
from repository.repositories import appointment_repository
from repository.repositories.settings_repository import appointment_duration_minutes


def schedule_appointment(data):
    scheduled_for = parse_datetime(data.get("scheduled_for", ""))
    if not scheduled_for:
        raise ValidationError("Appointment date and time are required.", "scheduled_for")

    duration_minutes = appointment_duration_minutes()
    conflict = appointment_repository.find_conflicting_appointment(scheduled_for, duration_minutes)
    if conflict:
        conflict_time = timezone.localtime(conflict.scheduled_for)
        raise ValidationError(
            f"This time overlaps with {conflict.patient.full_name}'s appointment at "
            f"{conflict_time:%Y-%m-%d %H:%M}.",
            "scheduled_for",
        )

    patient, _created = register_or_update_patient(data)
    payload = dict(data)
    payload["department"] = patient.department
    payload["scheduled_for"] = scheduled_for
    return appointment_repository.create_appointment(patient, payload)
