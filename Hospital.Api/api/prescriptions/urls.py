from django.urls import path

from . import views

urlpatterns = [
    path("", views.prescriptions_collection, name="prescriptions_collection"),
    path("<int:prescription_id>/print/", views.prescription_print, name="prescription_print"),
]
