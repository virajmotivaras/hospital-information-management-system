from datetime import timedelta

from django.utils import timezone

from repository.models import Appointment, Visit


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


def check_in_todays_scheduled_appointments():
    now = timezone.localtime()
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)

    appointments = (
        Appointment.objects.select_related("patient")
        .filter(
            status=Appointment.Status.SCHEDULED,
            scheduled_for__gte=day_start,
            scheduled_for__lt=day_end,
        )
        .order_by("scheduled_for")
    )

    active_statuses = [Visit.Status.WAITING, Visit.Status.IN_CONSULTATION]
    for appointment in appointments:
        active_visit = Visit.objects.filter(
            patient=appointment.patient,
            status__in=active_statuses,
            check_in_time__gte=day_start,
            check_in_time__lt=day_end,
        ).exists()
        if active_visit:
            appointment.status = Appointment.Status.CHECKED_IN
            appointment.save(update_fields=["status"])
            continue

        visit_type = Visit.VisitType.REPEAT if appointment.patient.visits.exists() else Visit.VisitType.NEW
        Visit.objects.create(
            patient=appointment.patient,
            visit_type=visit_type,
            department=appointment.department,
            reason=appointment.reason,
        )
        appointment.status = Appointment.Status.CHECKED_IN
        appointment.save(update_fields=["status"])


def waiting_queue():
    check_in_todays_scheduled_appointments()
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
