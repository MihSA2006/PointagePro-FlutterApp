from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee, Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]


@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    list_display  = ["email", "full_name", "department", "role", "is_active"]
    list_filter   = ["role", "department", "is_active"]
    search_fields = ["email", "first_name", "last_name"]
    ordering      = ["last_name"]

    fieldsets = (
        (None,           {"fields": ("email", "password")}),
        ("Informations", {"fields": ("first_name", "last_name", "department")}),
        ("Rôle",         {"fields": ("role", "is_active", "is_staff")}),
        ("Permissions",  {"fields": ("groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields":  ("email", "first_name", "last_name",
                        "department", "role", "password1", "password2"),
        }),
    )