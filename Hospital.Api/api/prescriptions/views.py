from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from api.common import handle_api_errors, parse_json, require_roles
from api.serializers import prescription_to_dict
from domain.common.roles import ADMIN, DOCTOR
from domain.prescriptions.services import write_prescription
from repository.repositories import prescription_repository
from repository.repositories.settings_repository import get_hospital_profile


@csrf_exempt
@require_roles(ADMIN, DOCTOR)
@handle_api_errors
def prescriptions_collection(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed."}, status=405)

    prescription = write_prescription(parse_json(request))
    return JsonResponse(
        {
            "prescription": prescription_to_dict(prescription),
            "print_url": f"/api/prescriptions/{prescription.id}/print/",
        },
        status=201,
    )


@login_required
@require_roles(ADMIN, DOCTOR)
def prescription_print(request, prescription_id):
    prescription = prescription_repository.get_prescription(prescription_id)
    return render(
        request,
        "prescription_print.html",
        {"prescription": prescription, "hospital": get_hospital_profile()},
    )
