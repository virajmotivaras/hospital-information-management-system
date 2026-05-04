from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.common import handle_api_errors, parse_json, require_roles
from api.serializers import visit_to_dict
from domain.common.roles import has_any_role
from domain.common.roles import ADMIN, DOCTOR, RECEPTION
from domain.patients.services import quick_check_in
from repository.models import Visit
from repository.repositories import visit_repository


@csrf_exempt
@require_roles(ADMIN, DOCTOR, RECEPTION)
@handle_api_errors
def visits_collection(request):
    if request.method == "POST" and not has_any_role(request.user, [ADMIN, RECEPTION]):
        return JsonResponse({"error": "Only Reception or Admin can check in patients."}, status=403)

    if request.method == "GET":
        visits = visit_repository.waiting_queue()
        return JsonResponse({"visits": [visit_to_dict(visit) for visit in visits]})

    if request.method == "POST":
        patient, visit = quick_check_in(parse_json(request))
        return JsonResponse(
            {
                "patient_id": patient.id,
                "visit": visit_to_dict(visit),
                "message": "Patient checked in.",
            },
            status=201,
        )

    return JsonResponse({"error": "Method not allowed."}, status=405)


@csrf_exempt
@require_roles(ADMIN, DOCTOR)
@handle_api_errors
def visit_status(request, visit_id):
    if request.method != "PATCH":
        return JsonResponse({"error": "Method not allowed."}, status=405)

    status = parse_json(request).get("status")
    valid_statuses = {choice[0] for choice in Visit.Status.choices}
    if status not in valid_statuses:
        return JsonResponse({"error": "Choose a valid visit status."}, status=400)

    visit = visit_repository.set_visit_status(visit_id, status)
    return JsonResponse({"visit": visit_to_dict(visit)})


@csrf_exempt
@require_roles(ADMIN, DOCTOR)
@handle_api_errors
def visit_vitals(request, visit_id):
    if request.method != "PATCH":
        return JsonResponse({"error": "Method not allowed."}, status=405)

    visit = visit_repository.update_visit_vitals(visit_id, parse_json(request))
    return JsonResponse({"visit": visit_to_dict(visit)})
