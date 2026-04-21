from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
import secrets


# ─── QRCodeSession ────────────────────────────────────────────────────────────
class QRCodeSession(models.Model):
    """
    Représente un QR Code généré par un admin.
    Chaque QR Code est à usage unique, typé (CHECK_IN / CHECK_OUT),
    et a une date d'expiration stricte.
    """

    class QRType(models.TextChoices):
        CHECK_IN  = "CHECK_IN",  "Entrée"
        CHECK_OUT = "CHECK_OUT", "Sortie"

    # ── Identification ──
    token       = models.CharField(
        max_length=64,
        unique=True,
        editable=False  # Jamais modifiable manuellement
    )
    type        = models.CharField(
        max_length=10,
        choices=QRType.choices
    )

    # ── Acteur ──
    created_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="qr_codes_created",
        limit_choices_to={"role": "admin"}  # Seuls les admins peuvent créer
    )

    # ── Expiration ──
    expires_at  = models.DateTimeField()

    # ── Timestamp ──
    created_at  = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "qr_code_sessions"
        verbose_name = "Session QR Code"
        verbose_name_plural = "Sessions QR Code"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        # Génération automatique du token à la création
        if not self.token:
            self.token = secrets.token_urlsafe(48)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"QR [{self.type}] - expire {self.expires_at}"

    # ── Méthodes métier ──
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        """Un QR Code est valide s'il n'est pas expiré."""
        return not self.is_expired


# ─── Attendance (TimeEntry) ───────────────────────────────────────────────────
class Attendance(models.Model):
    """
    Enregistrement de présence d'un employé pour une journée.
    - check_in_time  : heure d'arrivée (obligatoire)
    - check_out_time : heure de départ (nullable → pointage en cours)
    - work_duration  : calculé AUTOMATIQUEMENT (jamais saisi)
    - late_minutes   : calculé AUTOMATIQUEMENT au check-in
    - status         : ACTIVE (en cours) / COMPLETED (terminé)
    """

    class Status(models.TextChoices):
        ACTIVE    = "active",    "En cours"
        COMPLETED = "completed", "Terminé"

    # ── Relations ──
    employee        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendances"
    )

    # ── Pointage ──
    check_in_time   = models.DateTimeField()
    check_out_time  = models.DateTimeField(null=True, blank=True)

    # ── Champs calculés (JAMAIS saisis manuellement) ──
    work_duration   = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Durée de travail en minutes (calculée automatiquement)"
    )
    late_minutes    = models.PositiveIntegerField(
        default=0,
        help_text="Minutes de retard (calculées automatiquement)"
    )

    # ── Dérivés ──
    date            = models.DateField(
        help_text="Date dérivée automatiquement du check_in_time"
    )
    status          = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    # ── Audit ──
    created_at      = models.DateTimeField(default=timezone.now)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendances"
        verbose_name = "Présence"
        verbose_name_plural = "Présences"
        ordering = ["-date", "-check_in_time"]
        # ⚠️ Règle : un seul check-in ACTIVE par employé par jour
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "date"],
                condition=models.Q(status="active"),
                name="unique_active_checkin_per_employee_per_day"
            )
        ]

    def __str__(self):
        return f"{self.employee.full_name} — {self.date} [{self.status}]"

    # ── Calculs automatiques ──
    def calculate_work_duration(self):
        """
        Calcule la durée de travail en minutes.
        Toujours positive. Appelé au check-out.
        """
        if self.check_in_time and self.check_out_time:
            delta = self.check_out_time - self.check_in_time
            total_minutes = int(delta.total_seconds() / 60)
            # Sécurité : durée toujours positive
            return max(0, total_minutes)
        return None

    def calculate_late_minutes(self):
        """
        Calcule le retard en minutes par rapport à l'heure de début de travail.
        Configuré dans settings.py (WORK_START_HOUR / WORK_START_MINUTE).
        """
        from django.conf import settings as django_settings

        work_start = self.check_in_time.replace(
            hour=django_settings.WORK_START_HOUR,
            minute=django_settings.WORK_START_MINUTE,
            second=0,
            microsecond=0
        )
        if self.check_in_time > work_start:
            delta = self.check_in_time - work_start
            return int(delta.total_seconds() / 60)
        return 0

    # ── Surcharge save ──
    def save(self, *args, **kwargs):
        # 1. Date toujours dérivée du check_in_time
        if self.check_in_time:
            self.date = self.check_in_time.date()

        # 2. Calcul du retard au check-in
        if self.check_in_time and self.late_minutes == 0:
            self.late_minutes = self.calculate_late_minutes()

        # 3. Calcul automatique work_duration au check-out
        if self.check_out_time:
            self.work_duration = self.calculate_work_duration()
            self.status = self.Status.COMPLETED

        super().save(*args, **kwargs)

    # ── Validation ──
    def clean(self):
        # check_out toujours après check_in
        if self.check_in_time and self.check_out_time:
            if self.check_out_time <= self.check_in_time:
                raise ValidationError(
                    "L'heure de sortie doit être postérieure à l'heure d'entrée."
                )

    # ── Propriétés utiles ──
    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE

    @property
    def work_duration_display(self):
        """Affiche la durée en format HH:MM."""
        if self.work_duration is not None:
            hours = self.work_duration // 60
            minutes = self.work_duration % 60
            return f"{hours:02d}h{minutes:02d}"
        return "En cours"