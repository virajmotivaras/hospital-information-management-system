import json

from django.http import JsonResponse

from domain.common.errors import ValidationError
from domain.common.roles import has_any_role


def parse_json(request):
    if not request.body:
        return {}
    return json.loads(request.body.decode("utf-8"))


def api_error(message, status=400, field=None):
    payload = {"error": message}
    if field:
        payload["field"] = field
    return JsonResponse(payload, status=status)


def handle_api_errors(func):
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except ValidationError as exc:
            return api_error(exc.message, field=exc.field)
        except json.JSONDecodeError:
            return api_error("Request body must be valid JSON.")

    return wrapper


def require_roles(*roles):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Login required."}, status=401)
            if not has_any_role(request.user, roles):
                return JsonResponse({"error": "You do not have access to this action."}, status=403)
            return func(request, *args, **kwargs)

        return wrapper

    return decorator
