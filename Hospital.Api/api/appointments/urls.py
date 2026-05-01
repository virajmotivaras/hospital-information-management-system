from django.urls import path

from . import views

urlpatterns = [
    path("", views.appointments_collection, name="appointments_collection"),
]
