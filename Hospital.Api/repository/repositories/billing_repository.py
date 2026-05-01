from decimal import Decimal

from repository.models import Bill, BillLineItem


def list_bills_for_patient(patient_id):
    return list(
        Bill.objects.select_related("patient", "visit")
        .prefetch_related("items")
        .filter(patient_id=patient_id)
        .order_by("-created_at")
    )


def create_bill(patient, visit, data):
    bill = Bill.objects.create(
        patient=patient,
        visit=visit,
        paid_amount=Decimal(str(data.get("paid_amount") or "0.00")),
        notes=data.get("notes", ""),
    )
    for item in data.get("items", []):
        if item.get("description"):
            BillLineItem.objects.create(
                bill=bill,
                description=item["description"].strip(),
                quantity=Decimal(str(item.get("quantity") or "1")),
                unit_price=Decimal(str(item.get("unit_price") or "0")),
            )
    bill.refresh_status_from_amounts()
    bill.save(update_fields=["status", "updated_at"])
    return bill
