from django.db import transaction
from django.utils.dateparse import parse_date

from domain.common.errors import ValidationError
from repository.repositories import patient_repository, prescription_repository, visit_repository


def write_prescription(data):
    if not data.get("patient_id"):
        raise ValidationError("Select a patient before writing a prescription.", "patient_id")
    if not (data.get("doctor_name") or "").strip():
        raise ValidationError("Doctor name is required.", "doctor_name")

    patient = patient_repository.get_patient(data["patient_id"])
    visit = visit_repository.get_visit(data["visit_id"]) if data.get("visit_id") else None
    if visit and visit.patient_id != patient.id:
        raise ValidationError("Selected visit does not belong to this patient.", "visit_id")

    items = [item for item in data.get("items", []) if item.get("medicine_name")]
    if not items:
        raise ValidationError("Add at least one medicine.", "items")

    payload = dict(data)
    payload["items"] = items
    if payload.get("follow_up_date"):
        follow_up_date = parse_date(payload["follow_up_date"])
        if not follow_up_date:
            raise ValidationError("Use YYYY-MM-DD for follow-up date.", "follow_up_date")
        payload["follow_up_date"] = follow_up_date

    with transaction.atomic():
        prescription = prescription_repository.create_prescription(patient, visit, payload)
        if visit:
            visit.status = "COMPLETED"
            visit.save(update_fields=["status", "updated_at"])
    return prescription
