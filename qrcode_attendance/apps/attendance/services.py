from django.utils import timezone
from django.db import transaction
from datetime import datetime, time
from .models import Attendance, QRCodeSession


class QRCodeService:
    """Logique de validation des QR Codes."""

    @staticmethod
    def validate_token(token: str, expected_type: str = None) -> QRCodeSession:
        """
        Valide un token QR Code :
        1. Existe ?
        2. Bon type (si spécifié) ?
        3. Non expiré ?
        Retourne le QRCodeSession ou lève ValueError.
        """
        try:
            qr = QRCodeSession.objects.get(token=token)
        except QRCodeSession.DoesNotExist:
            raise ValueError("QR Code invalide ou introuvable.")

        if expected_type and qr.type != expected_type:
            raise ValueError(
                f"Ce QR Code est de type '{qr.type}'. "
                f"Un QR Code '{expected_type}' est attendu."
            )
        if qr.is_expired:
            raise ValueError("Ce QR Code a expiré.")

        return qr


class AttendanceService:
    """Logique métier des pointages."""

    @staticmethod
    @transaction.atomic
    def process_scan(employee, token: str) -> Attendance:
        """
        Traitement générique d'un scan QR Code :
        Identifie automatiquement s'il s'agit d'un check-in ou check-out
        grâce au type contenu dans la session du token.
        """
        # ── 1. Validation QR (sans type imposé au départ) ──
        qr = QRCodeService.validate_token(token)

        # ── 2. Routage selon le type ──
        if qr.type == QRCodeSession.QRType.CHECK_IN:
            return AttendanceService.process_checkin(employee, token)
        elif qr.type == QRCodeSession.QRType.CHECK_OUT:
            return AttendanceService.process_checkout(employee, token)
        else:
            raise ValueError(f"Type de QR Code '{qr.type}' non reconnu.")

    @staticmethod
    @transaction.atomic
    def process_checkin(employee, token: str) -> Attendance:
        """
        Traitement complet du check-in :
        1. Valide le QR Code
        2. Vérifie qu'il n'y a pas déjà un check-in actif
        3. Crée l'enregistrement Attendance
        """
        # ── 1. Validation QR ──
        qr = QRCodeService.validate_token(token, QRCodeSession.QRType.CHECK_IN)

        # ── 2. Vérification unicité check-in actif ──
        today = timezone.localdate()
        active_checkin = Attendance.objects.filter(
            employee=employee,
            date=today,
            status=Attendance.Status.ACTIVE
        ).exists()

        if active_checkin:
            raise ValueError(
                "Vous avez déjà un check-in actif aujourd'hui. "
                "Effectuez d'abord un check-out."
            )

        # ── 3. Création Attendance ──
        # Le save() calcule automatiquement late_minutes et date
        attendance = Attendance(
            employee      = employee,
            check_in_time = timezone.now(),
        )
        attendance.save()

        return attendance

    @staticmethod
    @transaction.atomic
    def process_checkout(employee, token: str) -> Attendance:
        """
        Traitement complet du check-out :
        1. Valide le QR Code
        2. Récupère le check-in actif
        3. Enregistre check-out et calcule work_duration
        """
        # ── 1. Validation QR ──
        qr = QRCodeService.validate_token(token, QRCodeSession.QRType.CHECK_OUT)

        # ── 2. Récupération check-in actif ──
        today = timezone.localdate()
        try:
            attendance = Attendance.objects.get(
                employee=employee,
                date=today,
                status=Attendance.Status.ACTIVE
            )
        except Attendance.DoesNotExist:
            raise ValueError(
                "Aucun check-in actif trouvé pour aujourd'hui. "
                "Effectuez d'abord un check-in."
            )

        # ── 3. Enregistrement check-out ──
        # Le save() calcule automatiquement work_duration et passe status → COMPLETED
        attendance.check_out_time = timezone.now()
        attendance.save()

        return attendance

    @staticmethod
    @transaction.atomic
    def auto_checkout_midnight():
        """
        Appelé par une tâche cron (ex: à 00:01).
        Tous les check-ins encore ACTIVE (des jours précédents) 
        reçoivent un check-out automatique à 23:59:59 de leur jour respectif.
        """
        active_attendances = Attendance.objects.filter(
            status=Attendance.Status.ACTIVE
        )

        count = 0
        for attendance in active_attendances:
            # On clôture à 23:59:59 du jour du check-in
            attendance.check_out_time = timezone.make_aware(
                datetime.combine(attendance.date, time(23, 59, 59))
            )
            attendance.save()
            count += 1

        return count