from django.urls import path

from . import views

urlpatterns = [
    path("", views.visits_collection, name="visits_collection"),
    path("<int:visit_id>/status/", views.visit_status, name="visit_status"),
]
