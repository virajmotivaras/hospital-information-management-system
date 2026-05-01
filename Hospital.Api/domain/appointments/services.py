from django.utils.dateparse import parse_datetime

from domain.common.errors import ValidationError
from domain.patients.services import register_or_update_patient
from repository.repositories import appointment_repository


def schedule_appointment(data):
    scheduled_for = parse_datetime(data.get("scheduled_for", ""))
    if not scheduled_for:
        raise ValidationError("Appointment date and time are required.", "scheduled_for")

    patient, _created = register_or_update_patient(data)
    payload = dict(data)
    payload["department"] = patient.department
    payload["scheduled_for"] = scheduled_for
    return appointment_repository.create_appointment(patient, payload)
