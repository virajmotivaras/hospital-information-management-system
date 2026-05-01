from django.http import JsonResponse

from api.common import require_roles
from api.serializers import department_to_dict
from domain.common.roles import ADMIN, DOCTOR, RECEPTION, user_roles
from repository.repositories.settings_repository import active_departments, get_hospital_profile


def session_context(request):
    if not request.user.is_authenticated:
        return JsonResponse({"authenticated": False}, status=401)

    profile = get_hospital_profile()
    return JsonResponse(
        {
            "authenticated": True,
            "user": {
                "username": request.user.username,
                "roles": user_roles(request.user),
            },
            "permissions": {
                "calendar": request.user.is_superuser or any(role in user_roles(request.user) for role in [ADMIN, DOCTOR, RECEPTION]),
                "desk": request.user.is_superuser or any(role in user_roles(request.user) for role in [ADMIN, RECEPTION]),
                "patients": request.user.is_superuser or any(role in user_roles(request.user) for role in [ADMIN, DOCTOR, RECEPTION]),
                "appointments": request.user.is_superuser or any(role in user_roles(request.user) for role in [ADMIN, RECEPTION]),
                "prescription": request.user.is_superuser or any(role in user_roles(request.user) for role in [ADMIN, DOCTOR]),
                "billing": request.user.is_superuser or any(role in user_roles(request.user) for role in [ADMIN, RECEPTION]),
                "admin": request.user.is_superuser or ADMIN in user_roles(request.user),
            },
            "hospital": {
                "name": profile.hospital_name,
                "tagline": profile.tagline,
                "logo_url": profile.logo.url if profile.logo else "",
                "address": profile.address,
                "phone_number": profile.phone_number,
            },
            "departments": [department_to_dict(department) for department in active_departments()],
        }
    )


@require_roles(ADMIN)
def admin_only_probe(request):
    return JsonResponse({"ok": True})
