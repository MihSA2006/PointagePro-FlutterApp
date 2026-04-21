from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from apps.core.permissions import IsAdminRole, IsOwnerOrAdmin
from apps.core.utils import success_response, error_response, get_today
from .models import Attendance, QRCodeSession
from .serializers import (
    AttendanceSerializer,
    AttendanceHistorySerializer,
    QRCodeCreateSerializer,
    QRCodeDetailSerializer,
    QRScanSerializer,
)
from .services import AttendanceService, QRCodeService


# ─── Attendance Scan View ─────────────────────────────────────────────────────
class AttendanceScanView(APIView):
    """
    POST /api/attendance/scan/
    L'employé scanne un QR Code (Check-in ou Check-out).
    Le type de pointage est détecté automatiquement via le token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QRScanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]

        try:
            attendance = AttendanceService.process_scan(
                employee=request.user,
                token=token
            )
            # On détermine le message de succès selon le statut final
            message = "Pointage enregistré avec succès."
            if attendance.status == Attendance.Status.COMPLETED:
                message = "Check-out enregistré avec succès."
            else:
                message = "Check-in enregistré avec succès."

            return Response(
                success_response(
                    message,
                    AttendanceSerializer(attendance).data
                ),
                status=status.HTTP_200_OK if attendance.status == Attendance.Status.COMPLETED else status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                error_response(str(e)),
                status=status.HTTP_400_BAD_REQUEST
            )


# ─── Attendance History View ──────────────────────────────────────────────────

class AttendanceHistoryView(APIView):
    """
    GET /api/attendance/history/
    Un employé voit son propre historique.
    Un admin peut voir l'historique de n'importe qui.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Admin peut filtrer par employee_id
        if user.role == "admin":
            employee_id = request.query_params.get("employee_id")
            if employee_id:
                qs = Attendance.objects.filter(
                    employee_id=employee_id
                ).select_related("employee__department")
            else:
                qs = Attendance.objects.all().select_related("employee__department")
        else:
            # Employee voit seulement ses propres pointages
            qs = Attendance.objects.filter(
                employee=user
            ).select_related("employee__department")

        # ── Filtres optionnels ──
        date_from = request.query_params.get("date_from")
        date_to   = request.query_params.get("date_to")
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)

        # Filtre par statut
        att_status = request.query_params.get("status")
        if att_status:
            qs = qs.filter(status=att_status)

        qs = qs.order_by("-date", "-check_in_time")

        serializer = AttendanceHistorySerializer(qs, many=True)
        return Response({
            "count":   qs.count(),
            "results": serializer.data
        })


# ─── QR Code ViewSet (Admin) ──────────────────────────────────────────────────

class QRCodeViewSet(viewsets.ModelViewSet):
    """
    CRUD QR Codes — Admin uniquement.
    GET    /api/attendance/qrcodes/         → liste
    POST   /api/attendance/qrcodes/         → créer
    GET    /api/attendance/qrcodes/{id}/    → détail
    DELETE /api/attendance/qrcodes/{id}/    → supprimer
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ["type", "is_used"]
    ordering           = ["-created_at"]

    def get_queryset(self):
        return QRCodeSession.objects.select_related(
            "created_by", "used_by"
        ).all()

    def get_serializer_class(self):
        if self.action == "create":
            return QRCodeCreateSerializer
        return QRCodeDetailSerializer

    def perform_create(self, serializer):
        serializer.save()  # created_by géré dans le serializer via request.user

    # ── GET /api/attendance/qrcodes/valid/ ──
    @action(detail=False, methods=["get"], url_path="valid")
    def valid_qrcodes(self, request):
        """Retourne uniquement les QR Codes encore valides (non expirés, non utilisés)."""
        now = timezone.now()
        qs  = self.get_queryset().filter(
            is_used=False,
            expires_at__gt=now
        )
        serializer = QRCodeDetailSerializer(qs, many=True)
        return Response({"count": qs.count(), "results": serializer.data})


# ─── Admin Attendance ViewSet ─────────────────────────────────────────────────

class AdminAttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lecture seule des pointages — Admin uniquement.
    GET /api/admin/attendance/
    GET /api/admin/attendance/{id}/
    Filtres : department, employee, date, status
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class   = AttendanceSerializer
    filter_backends    = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields   = ["status", "date", "employee__department"]
    search_fields      = [
        "employee__first_name",
        "employee__last_name",
        "employee__email"
    ]
    ordering_fields    = ["date", "check_in_time", "work_duration", "late_minutes"]
    ordering           = ["-date"]

    def get_queryset(self):
        qs = Attendance.objects.select_related(
            "employee__department"
        ).all()

        # ── Filtres supplémentaires ──
        params = self.request.query_params

        dept_id     = params.get("department_id")
        employee_id = params.get("employee_id")
        date_from   = params.get("date_from")
        date_to     = params.get("date_to")
        is_late     = params.get("is_late")      # "true" → uniquement les retards

        if dept_id:
            qs = qs.filter(employee__department_id=dept_id)
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        if is_late and is_late.lower() == "true":
            qs = qs.filter(late_minutes__gt=0)

        return qs

    # ── GET /api/admin/attendance/today/ ──
    @action(detail=False, methods=["get"], url_path="today")
    def today(self, request):
        """Tous les pointages du jour."""
        qs = self.get_queryset().filter(date=get_today())
        serializer = self.get_serializer(qs, many=True)
        return Response({"count": qs.count(), "results": serializer.data})

    # ── GET /api/admin/attendance/stats/ ──
    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        """Statistiques globales (aujourd'hui)."""
        today = get_today()
        qs    = Attendance.objects.filter(date=today)

        total_present  = qs.count()
        total_late     = qs.filter(late_minutes__gt=0).count()
        total_active   = qs.filter(status=Attendance.Status.ACTIVE).count()
        total_completed = qs.filter(status=Attendance.Status.COMPLETED).count()

        return Response({
            "date":             str(today),
            "total_present":    total_present,
            "total_late":       total_late,
            "total_active":     total_active,
            "total_completed":  total_completed,
        })