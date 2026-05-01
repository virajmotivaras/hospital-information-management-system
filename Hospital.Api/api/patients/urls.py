from django.urls import path

from . import views

urlpatterns = [
    path("", views.patients_collection, name="patients_collection"),
    path("<int:patient_id>/history/", views.patient_history, name="patient_history"),
    path("<int:patient_id>/bills/", views.patient_bills, name="patient_bills"),
]
