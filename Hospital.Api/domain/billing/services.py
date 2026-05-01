from decimal import Decimal, InvalidOperation

from domain.common.errors import ValidationError
from repository.repositories import billing_repository, patient_repository, visit_repository


def _money(value, field):
    try:
        amount = Decimal(str(value or "0"))
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError("Enter a valid amount.", field) from exc
    if amount < 0:
        raise ValidationError("Amount cannot be negative.", field)
    return amount


def create_patient_bill(patient_id, data):
    patient = patient_repository.get_patient(patient_id)
    visit = visit_repository.get_visit(data["visit_id"]) if data.get("visit_id") else None

    items = data.get("items") or []
    cleaned_items = []
    for item in items:
        description = (item.get("description") or "").strip()
        if not description:
            continue
        quantity = _money(item.get("quantity") or "1", "quantity")
        unit_price = _money(item.get("unit_price"), "unit_price")
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.", "quantity")
        cleaned_items.append(
            {
                "description": description,
                "quantity": quantity,
                "unit_price": unit_price,
            }
        )

    if not cleaned_items:
        raise ValidationError("Add at least one bill item.", "items")

    payload = {
        "visit_id": data.get("visit_id"),
        "paid_amount": _money(data.get("paid_amount"), "paid_amount"),
        "notes": data.get("notes", ""),
        "items": cleaned_items,
    }
    return billing_repository.create_bill(patient, visit, payload)
