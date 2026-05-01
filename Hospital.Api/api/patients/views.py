from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.common import handle_api_errors, parse_json, require_roles
from api.serializers import appointment_to_dict, bill_to_dict, patient_to_dict, prescription_to_dict
from domain.billing.services import create_patient_bill
from domain.common.roles import ADMIN, DOCTOR, RECEPTION, has_any_role
from domain.patients.services import register_or_update_patient
from repository.repositories import appointment_repository, billing_repository, patient_repository, prescription_repository


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


@require_roles(ADMIN, DOCTOR, RECEPTION)
@handle_api_errors
def patient_history(request, patient_id):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed."}, status=405)

    patient = patient_repository.get_patient(patient_id)
    payload = {
        "patient": patient_to_dict(patient),
        "appointments": {
            "upcoming": [appointment_to_dict(item) for item in appointment_repository.upcoming_for_patient(patient_id)],
            "past": [appointment_to_dict(item) for item in appointment_repository.past_for_patient(patient_id)],
        },
    }
    if has_any_role(request.user, [ADMIN, DOCTOR]):
        prescriptions = prescription_repository.list_prescriptions_for_patient(patient_id)
        payload["prescriptions"] = [
            {
                **prescription_to_dict(prescription),
                "print_url": f"/api/prescriptions/{prescription.id}/print/",
            }
            for prescription in prescriptions
        ]
    else:
        payload["prescriptions"] = []

    if has_any_role(request.user, [ADMIN, RECEPTION]):
        payload["bills"] = [bill_to_dict(bill) for bill in billing_repository.list_bills_for_patient(patient_id)]
    else:
        payload["bills"] = []

    return JsonResponse(payload)


@csrf_exempt
@require_roles(ADMIN, RECEPTION)
@handle_api_errors
def patient_bills(request, patient_id):
    if request.method == "GET":
        bills = billing_repository.list_bills_for_patient(patient_id)
        return JsonResponse({"bills": [bill_to_dict(bill) for bill in bills]})

    if request.method == "POST":
        bill = create_patient_bill(patient_id, parse_json(request))
        return JsonResponse({"bill": bill_to_dict(bill)}, status=201)

    return JsonResponse({"error": "Method not allowed."}, status=405)
