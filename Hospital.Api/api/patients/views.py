from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.common import handle_api_errors, parse_json, require_roles
from api.serializers import patient_to_dict
from domain.common.roles import ADMIN, DOCTOR, RECEPTION
from domain.patients.services import register_or_update_patient
from repository.repositories import patient_repository


@csrf_exempt
@require_roles(ADMIN, DOCTOR, RECEPTION)
@handle_api_errors
def patients_collection(request):
    if request.method == "GET":
        patients = patient_repository.list_patients(request.GET.get("search", ""))
        return JsonResponse({"patients": [patient_to_dict(patient) for patient in patients]})

    if request.method == "POST":
        patient, created = register_or_update_patient(parse_json(request))
        return JsonResponse({"patient": patient_to_dict(patient), "created": created}, status=201 if created else 200)

    return JsonResponse({"error": "Method not allowed."}, status=405)
