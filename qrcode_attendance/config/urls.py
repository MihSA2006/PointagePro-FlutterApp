from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # ── Authentification ──
    path("api/auth/",        include("apps.authentication.urls")),

    # ── Ressources ──
    path("api/employees/",   include("apps.employees.urls")),
    path("api/attendance/",  include("apps.attendance.urls")),

    # ── Admin métier ──
    path("api/admin/",       include("apps.attendance.urls_admin")),
]