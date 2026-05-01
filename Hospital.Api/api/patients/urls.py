from django.urls import path

from . import views

urlpatterns = [
    path("", views.patients_collection, name="patients_collection"),
]
