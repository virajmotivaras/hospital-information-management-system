def patient_to_dict(patient):
    return {
        "id": patient.id,
        "full_name": patient.full_name,
        "phone_number": patient.phone_number,
        "age_years": patient.age_years,
        "gender": patient.gender,
        "guardian_name": patient.guardian_name,
        "department": patient.department,
        "address": patient.address,
        "allergies": patient.allergies,
        "notes": patient.notes,
    }


def visit_to_dict(visit):
    return {
        "id": visit.id,
        "patient": patient_to_dict(visit.patient),
        "visit_type": visit.visit_type,
        "department": visit.department,
        "reason": visit.reason,
        "status": visit.status,
        "temperature_c": str(visit.temperature_c) if visit.temperature_c is not None else "",
        "weight_kg": str(visit.weight_kg) if visit.weight_kg is not None else "",
        "blood_pressure": visit.blood_pressure,
        "check_in_time": visit.check_in_time.isoformat(),
    }


def appointment_to_dict(appointment):
    return {
        "id": appointment.id,
        "patient": patient_to_dict(appointment.patient),
        "department": appointment.department,
        "scheduled_for": appointment.scheduled_for.isoformat(),
        "reason": appointment.reason,
        "status": appointment.status,
    }


def prescription_to_dict(prescription):
    return {
        "id": prescription.id,
        "patient": patient_to_dict(prescription.patient),
        "visit_id": prescription.visit_id,
        "doctor_name": prescription.doctor_name,
        "diagnosis": prescription.diagnosis,
        "advice": prescription.advice,
        "follow_up_date": prescription.follow_up_date.isoformat() if prescription.follow_up_date else "",
        "created_at": prescription.created_at.isoformat(),
        "items": [
            {
                "medicine_name": item.medicine_name,
                "dosage": item.dosage,
                "frequency": item.frequency,
                "duration": item.duration,
                "instructions": item.instructions,
            }
            for item in prescription.items.all()
        ],
    }
