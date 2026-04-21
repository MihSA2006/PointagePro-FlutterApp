from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AttendanceScanView,
    AttendanceHistoryView,
    QRCodeViewSet,
)

router = DefaultRouter()
router.register(r"qrcodes", QRCodeViewSet, basename="qrcode")

urlpatterns = [
    # ── Pointage ──
    path("scan/",      AttendanceScanView.as_view(),    name="attendance-scan"),
    path("history/",   AttendanceHistoryView.as_view(), name="attendance-history"),

    # ── QR Codes (admin) ──
    path("", include(router.urls)),
]