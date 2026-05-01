from repository.models import Prescription, PrescriptionItem


def create_prescription(patient, visit, data):
    prescription = Prescription.objects.create(
        patient=patient,
        visit=visit,
        doctor_name=data["doctor_name"].strip(),
        diagnosis=data.get("diagnosis", ""),
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
