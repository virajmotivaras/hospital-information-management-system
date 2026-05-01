from domain.common.errors import ValidationError
from repository.models import Patient


VALID_DEPARTMENTS = {choice[0] for choice in Patient.Department.choices}
VALID_GENDERS = {choice[0] for choice in Patient.Gender.choices}


def clean_patient_payload(data, require_name=True):
    cleaned = dict(data)
    cleaned["full_name"] = (data.get("full_name") or "").strip()
    cleaned["department"] = data.get("department") or Patient.Department.GYNECOLOGY
    cleaned["gender"] = data.get("gender") or Patient.Gender.NOT_SPECIFIED

    if require_name and not cleaned["full_name"]:
        raise ValidationError("Patient name is required.", "full_name")
    if cleaned["department"] not in VALID_DEPARTMENTS:
        raise ValidationError("Choose gynecology or pediatrics.", "department")
    if cleaned["gender"] not in VALID_GENDERS:
        raise ValidationError("Choose a valid gender.", "gender")

    if cleaned.get("age_years") in ("", None):
        cleaned["age_years"] = None
    else:
        try:
            age = int(cleaned["age_years"])
        except (TypeError, ValueError) as exc:
            raise ValidationError("Age must be a number.", "age_years") from exc
        if age < 0 or age > 130:
            raise ValidationError("Age must be between 0 and 130.", "age_years")
        cleaned["age_years"] = age

    return cleaned
