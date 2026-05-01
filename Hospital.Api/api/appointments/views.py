from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.common import handle_api_errors, parse_json, require_roles
from api.serializers import appointment_to_dict
from domain.common.roles import ADMIN, RECEPTION
from domain.appointments.services import schedule_appointment
from repository.repositories import appointment_repository


@csrf_exempt
@require_roles(ADMIN, RECEPTION)
@handle_api_errors
def appointments_collection(request):
    if request.method == "GET":
        appointments = appointment_repository.upcoming_appointments()
        return JsonResponse({"appointments": [appointment_to_dict(item) for item in appointments]})

    if request.method == "POST":
        appointment = schedule_appointment(parse_json(request))
        return JsonResponse({"appointment": appointment_to_dict(appointment)}, status=201)

    return JsonResponse({"error": "Method not allowed."}, status=405)
