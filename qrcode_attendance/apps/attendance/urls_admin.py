from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminAttendanceViewSet

router = DefaultRouter()
router.register(r"attendance", AdminAttendanceViewSet, basename="admin-attendance")

urlpatterns = [
    path("", include(router.urls)),
]