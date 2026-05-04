from pathlib import Path
from pathlib import Path
from shutil import copy2
from types import MethodType

from django.conf import settings
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone

from repository.models import (
    Appointment,
    BackupRecord,
    Bill,
    BillLineItem,
    Department,
    HospitalProfile,
    Patient,
    Prescription,
    PrescriptionItem,
    StaffProfile,
    Visit,
)


def create_database_backup(profile, username):
    source = Path(settings.DATABASES["default"]["NAME"])
    target_dir = Path(profile.backup_folder_path)
    timestamp = timezone.localtime().strftime("%Y%m%d-%H%M%S")
    target = target_dir / f"hospital-db-{timestamp}.sqlite3"
    copy2(source, target)
    return BackupRecord.objects.create(
        source_database=str(source),
        backup_file=str(target),
        created_by=username,
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "display_order")
    list_filter = ("is_active",)
    search_fields = ("name", "code")


@admin.register(HospitalProfile)
class HospitalProfileAdmin(admin.ModelAdmin):
    list_display = (
        "hospital_name",
        "tagline",
        "appointment_duration_minutes",
        "include_prescription_print_header",
        "backup_folder_path",
        "updated_at",
    )
    actions = ["create_database_backup"]

    @admin.action(description="Create database backup now")
    def create_database_backup(self, request, queryset):
        for profile in queryset:
            if not profile.backup_folder_path:
                self.message_user(request, "Set a backup folder before running backup.", messages.ERROR)
                continue
            record = create_database_backup(profile, request.user.username)
            self.message_user(request, f"Backup created: {record.backup_file}", messages.SUCCESS)


@admin.register(BackupRecord)
class BackupRecordAdmin(admin.ModelAdmin):
    change_list_template = "repository/admin/backuprecord/change_list.html"
    list_display = ("created_at", "backup_file", "created_by")
    readonly_fields = ("created_at", "source_database", "backup_file", "created_by")

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "create-backup/",
                self.admin_site.admin_view(self.create_backup_view),
                name="repository_backuprecord_create_backup",
            ),
        ]
        return custom_urls + urls

    def create_backup_view(self, request):
        profile = HospitalProfile.objects.order_by("id").first()
        if not profile or not profile.backup_folder_path:
            self.message_user(
                request,
                "Set the backup folder path in Hospital profile before creating a backup.",
                messages.ERROR,
            )
            return redirect("admin:repository_hospitalprofile_changelist")

        record = create_database_backup(profile, request.user.username)
        self.message_user(request, f"Backup created: {record.backup_file}", messages.SUCCESS)
        return redirect("admin:repository_backuprecord_changelist")


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "must_change_password")
    list_filter = ("must_change_password",)
    search_fields = ("user__username",)


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 0


class BillLineItemInline(admin.TabularInline):
    model = BillLineItem
    extra = 0


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    search_fields = ("full_name", "phone_number", "guardian_name")
    list_display = ("full_name", "phone_number", "department", "age_years", "updated_at")
    list_filter = ("department", "gender")


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    search_fields = ("patient__full_name", "patient__phone_number", "reason")
    list_display = ("patient", "visit_type", "department", "status", "check_in_time")
    list_filter = ("department", "visit_type", "status")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    search_fields = ("patient__full_name", "patient__phone_number", "reason")
    list_display = ("patient", "department", "scheduled_for", "status")
    list_filter = ("department", "status")


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    search_fields = ("patient__full_name", "doctor_name", "symptoms", "diagnosis", "examination_findings")
    list_display = ("patient", "doctor_name", "created_at", "follow_up_date")
    inlines = [PrescriptionItemInline]


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    search_fields = ("patient__full_name", "patient__phone_number", "notes")
    list_display = ("patient", "status", "created_at", "paid_amount")
    list_filter = ("status", "created_at")
    inlines = [BillLineItemInline]


def admin_index_with_record_previews(site, request, extra_context=None):
    app_list = site.get_app_list(request)

    for app in app_list:
        for model in app["models"]:
            model_admin = site._registry.get(model["model"])
            if not model_admin or not model_admin.has_view_permission(request):
                model["record_previews"] = []
                continue

            objects = model_admin.get_queryset(request).order_by("-pk")[:5]
            model["record_previews"] = [
                {
                    "label": str(item),
                    "url": reverse(
                        f"admin:{item._meta.app_label}_{item._meta.model_name}_change",
                        args=[item.pk],
                        current_app=site.name,
                    ),
                }
                for item in objects
            ]

    context = {
        **site.each_context(request),
        "title": site.index_title,
        "subtitle": None,
        "app_list": app_list,
        **(extra_context or {}),
    }
    request.current_app = site.name
    return TemplateResponse(request, "repository/admin/index.html", context)


admin.site.index = MethodType(admin_index_with_record_previews, admin.site)
