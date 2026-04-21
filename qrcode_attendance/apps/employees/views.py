from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.permissions import IsAdminRole, IsAdminOrReadOnly
from apps.core.utils import success_response, error_response
from .models import Employee, Department
from .serializers import (
    EmployeeListSerializer,
    EmployeeDetailSerializer,
    DepartmentSerializer,
)


# ─── Department ViewSet ───────────────────────────────────────────────────────

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    CRUD Départements.
    Lecture : admin + employee
    Écriture : admin uniquement
    """
    queryset           = Department.objects.all()
    serializer_class   = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ["name"]
    ordering_fields    = ["name"]
    ordering           = ["name"]

    def destroy(self, request, *args, **kwargs):
        department = self.get_object()
        # Empêcher suppression si des employés sont rattachés
        if department.employees.filter(is_active=True).exists():
            return Response(
                error_response(
                    "Impossible de supprimer ce département : "
                    "des employés actifs y sont rattachés."
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


# ─── Employee ViewSet ─────────────────────────────────────────────────────────

class EmployeeViewSet(viewsets.ModelViewSet):
    """
    CRUD Employés.
    - Liste / détail : admin uniquement
    - Un employé peut voir son propre profil via /me/
    """
    queryset         = Employee.objects.select_related("department").all()
    permission_classes = [IsAuthenticated, IsAdminRole]
    filter_backends  = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ["department", "role", "is_active"]
    search_fields    = ["first_name", "last_name", "email"]
    ordering_fields  = ["last_name", "created_at", "department"]
    ordering         = ["last_name"]

    def get_serializer_class(self):
        if self.action == "list":
            return EmployeeListSerializer
        return EmployeeDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # Filtre optionnel par département
        dept_id = self.request.query_params.get("department_id")
        if dept_id:
            qs = qs.filter(department_id=dept_id)
        return qs

    # ── GET /api/employees/me/ ──
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="me"
    )
    def me(self, request):
        """Retourne le profil de l'utilisateur connecté."""
        serializer = EmployeeDetailSerializer(request.user)
        return Response(serializer.data)

    # ── PATCH /api/employees/me/update/ ──
    @action(
        detail=False,
        methods=["patch"],
        permission_classes=[IsAuthenticated],
        url_path="me/update"
    )
    def update_me(self, request):
        """Permet à un employé de mettre à jour son propre profil."""
        serializer = EmployeeDetailSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        # Empêcher un employé de changer son propre rôle
        if "role" in request.data and request.user.role != "admin":
            return Response(
                error_response("Vous ne pouvez pas modifier votre propre rôle."),
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()
        return Response(
            success_response("Profil mis à jour.", serializer.data)
        )

    # ── POST /api/employees/{id}/deactivate/ ──
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsAdminRole],
        url_path="deactivate"
    )
    def deactivate(self, request, pk=None):
        """Désactiver un employé (soft delete)."""
        employee = self.get_object()
        if employee == request.user:
            return Response(
                error_response("Vous ne pouvez pas vous désactiver vous-même."),
                status=status.HTTP_400_BAD_REQUEST
            )
        employee.is_active = False
        employee.save(update_fields=["is_active"])
        return Response(
            success_response(f"{employee.full_name} a été désactivé.")
        )

    # ── POST /api/employees/{id}/activate/ ──
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsAdminRole],
        url_path="activate"
    )
    def activate(self, request, pk=None):
        """Réactiver un employé."""
        employee = self.get_object()
        employee.is_active = True
        employee.save(update_fields=["is_active"])
        return Response(
            success_response(f"{employee.full_name} a été réactivé.")
        )