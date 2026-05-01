from pathlib import Path
from shutil import copy2

from django.conf import settings
from django.contrib import admin, messages
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


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "display_order")
    list_filter = ("is_active",)
    search_fields = ("name", "code")


@admin.register(HospitalProfile)
class HospitalProfileAdmin(admin.ModelAdmin):
    list_display = ("hospital_name", "tagline", "backup_folder_path", "updated_at")
    actions = ["create_database_backup"]

    @admin.action(description="Create database backup now")
    def create_database_backup(self, request, queryset):
        for profile in queryset:
            if not profile.backup_folder_path:
                self.message_user(request, "Set a backup folder before running backup.", messages.ERROR)
                continue
            source = Path(settings.DATABASES["default"]["NAME"])
            target_dir = Path(profile.backup_folder_path)
            timestamp = timezone.localtime().strftime("%Y%m%d-%H%M%S")
            target = target_dir / f"hospital-db-{timestamp}.sqlite3"
            copy2(source, target)
            BackupRecord.objects.create(
                source_database=str(source),
                backup_file=str(target),
                created_by=request.user.username,
            )
            self.message_user(request, f"Backup created: {target}", messages.SUCCESS)


@admin.register(BackupRecord)
class BackupRecordAdmin(admin.ModelAdmin):
    list_display = ("created_at", "backup_file", "created_by")
    readonly_fields = ("created_at", "source_database", "backup_file", "created_by")

    def has_add_permission(self, request):
        return False


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
    search_fields = ("patient__full_name", "doctor_name", "diagnosis")
    list_display = ("patient", "doctor_name", "created_at", "follow_up_date")
    inlines = [PrescriptionItemInline]


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    search_fields = ("patient__full_name", "patient__phone_number", "notes")
    list_display = ("patient", "status", "created_at", "paid_amount")
    list_filter = ("status", "created_at")
    inlines = [BillLineItemInline]
