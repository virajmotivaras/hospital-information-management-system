from repository.repositories import patient_repository, visit_repository
from repository.models import Visit

from .rules import clean_patient_payload


def quick_check_in(data):
    cleaned = clean_patient_payload(data)
    patient = patient_repository.find_existing_patient(
        full_name=cleaned.get("full_name"),
        phone_number=cleaned.get("phone_number"),
        guardian_name=cleaned.get("guardian_name"),
    )
    visit_type = Visit.VisitType.REPEAT if patient else Visit.VisitType.NEW

    if patient:
        patient = patient_repository.update_patient_details(patient, cleaned)
    else:
        patient = patient_repository.create_patient(cleaned)

    visit = visit_repository.create_visit(patient, visit_type, cleaned)
    return patient, visit


def register_or_update_patient(data):
    cleaned = clean_patient_payload(data)
    patient = patient_repository.find_existing_patient(
        full_name=cleaned.get("full_name"),
        phone_number=cleaned.get("phone_number"),
        guardian_name=cleaned.get("guardian_name"),
    )
    if patient:
        return patient_repository.update_patient_details(patient, cleaned), False
    return patient_repository.create_patient(cleaned), True
