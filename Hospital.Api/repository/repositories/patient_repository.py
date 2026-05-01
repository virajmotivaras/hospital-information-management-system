from django.db.models import Q

from repository.models import Patient


def normalize_phone(phone_number):
    return "".join(ch for ch in (phone_number or "") if ch.isdigit())


def normalize_name(name):
    return " ".join((name or "").split())


def find_existing_patient(full_name="", phone_number="", guardian_name=""):
    phone = normalize_phone(phone_number)
    name = normalize_name(full_name)
    guardian = normalize_name(guardian_name)

    if phone and name:
        queryset = Patient.objects.filter(phone_number=phone, full_name__iexact=name)
        if guardian:
            queryset = queryset.filter(guardian_name__iexact=guardian)
        return queryset.order_by("-updated_at").first()

    if name and guardian:
        return Patient.objects.filter(
            full_name__iexact=name,
            guardian_name__iexact=guardian,
        ).order_by("-updated_at").first()

    return None


def create_patient(data):
    payload = {
        "full_name": data["full_name"].strip(),
        "phone_number": normalize_phone(data.get("phone_number")),
        "age_years": data.get("age_years") or None,
        "gender": data.get("gender") or Patient.Gender.NOT_SPECIFIED,
        "guardian_name": (data.get("guardian_name") or "").strip(),
        "department": data["department"],
        "address": data.get("address", ""),
        "allergies": data.get("allergies", ""),
        "notes": data.get("notes", ""),
    }
    return Patient.objects.create(**payload)


def update_patient_details(patient, data):
    fields = [
        "full_name",
        "age_years",
        "gender",
        "guardian_name",
        "department",
        "address",
        "allergies",
        "notes",
    ]
    for field in fields:
        if field in data and data[field] not in ("", None):
            setattr(patient, field, data[field])
    if data.get("phone_number"):
        patient.phone_number = normalize_phone(data["phone_number"])
    patient.save()
    return patient


def list_patients(search="", limit=50):
    queryset = Patient.objects.all().order_by("-updated_at")
    term = (search or "").strip()
    if term:
        queryset = queryset.filter(
            Q(full_name__icontains=term)
            | Q(phone_number__icontains=normalize_phone(term))
            | Q(guardian_name__icontains=term)
        )
    return list(queryset[:limit])


def get_patient(patient_id):
    return Patient.objects.get(id=patient_id)
