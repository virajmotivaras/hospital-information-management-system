from repository.models import Visit


def create_visit(patient, visit_type, data):
    return Visit.objects.create(
        patient=patient,
        visit_type=visit_type,
        department=data["department"],
        reason=data.get("reason", ""),
        temperature_c=data.get("temperature_c") or None,
        weight_kg=data.get("weight_kg") or None,
        blood_pressure=data.get("blood_pressure", ""),
    )


def waiting_queue():
    return list(
        Visit.objects.select_related("patient")
        .filter(status__in=[Visit.Status.WAITING, Visit.Status.IN_CONSULTATION])
        .order_by("check_in_time")
    )


def recent_visits(limit=30):
    return list(Visit.objects.select_related("patient").order_by("-check_in_time")[:limit])


def set_visit_status(visit_id, status):
    visit = Visit.objects.select_related("patient").get(id=visit_id)
    visit.status = status
    visit.save(update_fields=["status", "updated_at"])
    return visit


def get_visit(visit_id):
    return Visit.objects.select_related("patient").get(id=visit_id)
