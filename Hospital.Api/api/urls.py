from django.urls import include, path
from .session import session_context

urlpatterns = [
    path("session/", session_context, name="session_context"),
    path("patients/", include("api.patients.urls")),
    path("visits/", include("api.visits.urls")),
    path("appointments/", include("api.appointments.urls")),
    path("prescriptions/", include("api.prescriptions.urls")),
]
