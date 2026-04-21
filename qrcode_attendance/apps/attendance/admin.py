from django.contrib import admin
from .models import Attendance, QRCodeSession


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display  = [
        "employee", "date", "check_in_time",
        "check_out_time", "work_duration_display",
        "late_minutes", "status"
    ]
    list_filter   = ["status", "date", "employee__department"]
    search_fields = ["employee__first_name", "employee__last_name", "employee__email"]
    ordering      = ["-date"]
    readonly_fields = [
        "work_duration", "late_minutes",
        "date", "created_at", "updated_at"
    ]


@admin.register(QRCodeSession)
class QRCodeSessionAdmin(admin.ModelAdmin):
    list_display  = ["token", "type", "created_by", "expires_at", "created_at"]
    list_filter   = ["type"]
    search_fields = ["token", "created_by__email"]
    readonly_fields = ["token", "created_at"]