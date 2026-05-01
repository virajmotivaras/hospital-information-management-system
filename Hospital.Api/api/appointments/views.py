from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt

from api.common import handle_api_errors, parse_json, require_roles
from api.serializers import appointment_to_dict
from domain.common.roles import ADMIN, DOCTOR, RECEPTION, has_any_role
from domain.appointments.services import schedule_appointment
from repository.repositories import appointment_repository


@csrf_exempt
@require_roles(ADMIN, DOCTOR, RECEPTION)
@handle_api_errors
def appointments_collection(request):
    if request.method == "GET":
        start = parse_datetime(request.GET.get("start", ""))
        end = parse_datetime(request.GET.get("end", ""))
        if start and end:
            if timezone.is_naive(start):
                start = timezone.make_aware(start)
            if timezone.is_naive(end):
                end = timezone.make_aware(end)
            appointments = appointment_repository.appointments_between(start, end)
        else:
            appointments = appointment_repository.upcoming_appointments()
        return JsonResponse({"appointments": [appointment_to_dict(item) for item in appointments]})

    if request.method == "POST":
        if not has_any_role(request.user, [ADMIN, RECEPTION]):
            return JsonResponse({"error": "You do not have access to this action."}, status=403)
        appointment = schedule_appointment(parse_json(request))
        return JsonResponse({"appointment": appointment_to_dict(appointment)}, status=201)

    return JsonResponse({"error": "Method not allowed."}, status=405)
