from repository.models import Prescription, PrescriptionItem


def create_prescription(patient, visit, data):
    prescription = Prescription.objects.create(
        patient=patient,
        visit=visit,
        doctor_name=data["doctor_name"].strip(),
        symptoms=data.get("symptoms", ""),
        symptom_entries=data.get("symptom_entries", []),
        diagnosis=data.get("diagnosis", ""),
        examination_findings=data.get("examination_findings", ""),
        advice=data.get("advice", ""),
        follow_up_date=data.get("follow_up_date") or None,
    )
    for item in data.get("items", []):
        if item.get("medicine_name"):
            PrescriptionItem.objects.create(
                prescription=prescription,
                medicine_name=item["medicine_name"].strip(),
                dosage=item.get("dosage", ""),
                frequency=item.get("frequency", ""),
                duration=item.get("duration", ""),
                instructions=item.get("instructions", ""),
            )
    return prescription


def get_prescription(prescription_id):
    return (
        Prescription.objects.select_related("patient", "visit")
        .prefetch_related("items")
        .get(id=prescription_id)
    )


def list_prescriptions_for_patient(patient_id):
    return list(
        Prescription.objects.select_related("patient", "visit")
        .prefetch_related("items")
        .filter(patient_id=patient_id)
        .order_by("-created_at")
    )
