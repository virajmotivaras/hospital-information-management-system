from repository.models import Department, HospitalProfile


DEFAULT_DEPARTMENT = {"code": "GENERAL", "name": "General", "display_order": 1}


def get_hospital_profile():
    profile = HospitalProfile.objects.order_by("id").first()
    if profile:
        return profile
    return HospitalProfile.objects.create()


def ensure_default_department():
    department, _created = Department.objects.get_or_create(
        code=DEFAULT_DEPARTMENT["code"],
        defaults={
            "name": DEFAULT_DEPARTMENT["name"],
            "display_order": DEFAULT_DEPARTMENT["display_order"],
            "is_active": True,
        },
    )
    return department


def active_departments():
    if not Department.objects.filter(is_active=True).exists():
        ensure_default_department()
    return list(Department.objects.filter(is_active=True).order_by("display_order", "name"))


def default_department_code():
    departments = active_departments()
    return departments[0].code
