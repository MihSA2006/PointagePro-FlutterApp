from rest_framework import serializers
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from apps.core.utils import (
    compute_checkin_qr_expiry,
    compute_checkout_qr_expiry,
    minutes_to_display,
)
from .models import Attendance, QRCodeSession


# ─── QRCodeSession Serializers ────────────────────────────────────────────────

class QRCodeCreateSerializer(serializers.ModelSerializer):
    """
    Utilisé par l'admin pour générer un QR Code.
    Le token et expires_at sont calculés automatiquement.
    """

    class Meta:
        model  = QRCodeSession
        fields = ["id", "type", "token", "expires_at", "created_at"]
        read_only_fields = ["id", "token", "expires_at", "created_at"]

    def validate_type(self, value):
        allowed = [QRCodeSession.QRType.CHECK_IN, QRCodeSession.QRType.CHECK_OUT]
        if value not in allowed:
            raise serializers.ValidationError(
                f"Type invalide. Choisir parmi : {[t.value for t in QRCodeSession.QRType]}"
            )
        return value

    def validate(self, attrs):
        qr_type = attrs.get("type")
        today   = timezone.localdate()
        
        # Filtrage par plage horaire locale (évite les bugs UTC/local)
        local_now = timezone.localtime()
        today_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Vérifier si un QR Code de ce type existe déjà pour aujourd'hui
        exists = QRCodeSession.objects.filter(
            type=qr_type,
            created_at__gte=today_start,
            created_at__lt=today_end
        ).exists()
        
        if exists:
            raise serializers.ValidationError(
                f"Un QR Code de type '{qr_type}' a déjà été généré aujourd'hui. "
                "Un seul QR par type est autorisé par jour."
            )
        return attrs

    def create(self, validated_data):
        qr_type = validated_data["type"]
        admin   = self.context["request"].user

        # ── Calcul expiration selon le type ──
        if qr_type == QRCodeSession.QRType.CHECK_IN:
            expires_at = compute_checkin_qr_expiry(
                settings.WORK_START_HOUR,
                settings.WORK_START_MINUTE
            )
        else:
            expires_at = compute_checkout_qr_expiry()

        return QRCodeSession.objects.create(
            type       = qr_type,
            created_by = admin,
            expires_at = expires_at,
        )


class QRCodeDetailSerializer(serializers.ModelSerializer):
    """Lecture complète d'un QR Code (admin)."""
    created_by_name = serializers.CharField(
        source="created_by.full_name",
        read_only=True
    )
    is_expired  = serializers.BooleanField(read_only=True)
    is_valid    = serializers.BooleanField(read_only=True)

    class Meta:
        model  = QRCodeSession
        fields = [
            "id", "token", "type",
            "created_by", "created_by_name",
            "expires_at", 
            "is_expired", "is_valid",
            "created_at"
        ]
        read_only_fields = fields


# ─── Attendance Serializers ───────────────────────────────────────────────────

class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer principal pour les pointages.
    Tous les champs calculés sont en lecture seule.
    """
    employee_name    = serializers.CharField(
        source="employee.full_name",
        read_only=True
    )
    department_name  = serializers.CharField(
        source="employee.department.name",
        read_only=True
    )
    work_duration_display = serializers.SerializerMethodField()
    late_display          = serializers.SerializerMethodField()

    class Meta:
        model  = Attendance
        fields = [
            "id",
            "employee", "employee_name", "department_name",
            "date",
            "check_in_time", "check_out_time",
            "work_duration", "work_duration_display",
            "late_minutes", "late_display",
            "status",
            "created_at", "updated_at",
        ]
        # ⚠️ Champs calculés JAMAIS modifiables manuellement
        read_only_fields = [
            "id", "employee", "date",
            "work_duration", "late_minutes",
            "status", "created_at", "updated_at",
            "employee_name", "department_name",
        ]

    def get_work_duration_display(self, obj):
        return minutes_to_display(obj.work_duration)

    def get_late_display(self, obj):
        if obj.late_minutes == 0:
            return "À l'heure"
        return f"Retard : {minutes_to_display(obj.late_minutes)}"


class AttendanceHistorySerializer(serializers.ModelSerializer):
    """Serializer allégé pour l'historique (liste)."""
    work_duration_display = serializers.SerializerMethodField()
    is_late = serializers.SerializerMethodField()

    class Meta:
        model  = Attendance
        fields = [
            "id", "date",
            "check_in_time", "check_out_time",
            "work_duration", "work_duration_display",
            "late_minutes", "is_late",
            "status",
        ]
        read_only_fields = fields

    def get_work_duration_display(self, obj):
        return minutes_to_display(obj.work_duration)

    def get_is_late(self, obj):
        return obj.late_minutes > 0


# ─── QR Scan Serializers ──────────────────────────────────────────────────────

class QRScanSerializer(serializers.Serializer):
    """
    Serializer pour les requêtes de scan QR Code.
    L'employé envoie uniquement le token.
    """
    token = serializers.CharField(
        max_length=200,
        help_text="Token du QR Code scanné"
    )

    def validate_token(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Le token ne peut pas être vide.")
        return value.strip()