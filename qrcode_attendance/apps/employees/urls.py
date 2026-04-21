from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, DepartmentViewSet

router = DefaultRouter()
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"",            EmployeeViewSet,   basename="employee")

urlpatterns = [
    path("", include(router.urls)),
]