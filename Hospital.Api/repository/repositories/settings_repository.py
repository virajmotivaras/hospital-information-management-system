from repository.models import HospitalProfile


def get_hospital_profile():
    profile = HospitalProfile.objects.order_by("id").first()
    if profile:
        return profile
    return HospitalProfile.objects.create()
