from django.utils import timezone
from datetime import datetime, time


# ─── Helpers temporels ────────────────────────────────────────────────────────

def get_today():
    """Retourne la date du jour (timezone-aware)."""
    return timezone.localdate()


def get_now():
    """Retourne datetime maintenant (timezone-aware)."""
    return timezone.now()


def get_midnight_today():
    """
    Retourne minuit (fin de journée) aujourd'hui en timezone locale.
    Utilisé pour l'expiration des QR Code CHECK_OUT.
    """
    local_now = timezone.localtime(timezone.now())
    midnight = local_now.replace(hour=23, minute=59, second=59, microsecond=0)
    return midnight


def get_end_of_work_hour(work_start_hour: int, work_start_minute: int):
    """
    Retourne l'heure de fin de validité d'un QR Code CHECK_IN.
    Par défaut : heure de début de travail + 2h (tolérance).
    Exemple : si travail à 08h00, QR CHECK_IN expire à 10h00.
    """
    local_now = timezone.localtime(timezone.now())
    expiry = local_now.replace(
        hour=min(work_start_hour + 2, 23),
        minute=work_start_minute,
        second=0,
        microsecond=0
    )
    # Si l'heure d'expiration est déjà passée, on met à minuit
    if expiry < local_now:
        return get_midnight_today()
    return expiry


def minutes_to_display(minutes: int) -> str:
    """
    Convertit des minutes en string lisible.
    Exemple : 135 → '2h15'
    """
    if minutes is None:
        return "—"
    hours = minutes // 60
    mins  = minutes % 60
    if hours > 0:
        return f"{hours}h{mins:02d}"
    return f"{mins} min"


# ─── Helpers QR Code ──────────────────────────────────────────────────────────

def compute_checkin_qr_expiry(work_start_hour: int, work_start_minute: int):
    """
    Expiration d'un QR CHECK_IN :
    → Fin de la fenêtre d'arrivée (work_start + 2h)
    """
    return get_end_of_work_hour(work_start_hour, work_start_minute)


def compute_checkout_qr_expiry():
    """
    Expiration d'un QR CHECK_OUT :
    → Minuit (fin de journée)
    """
    return get_midnight_today()


# ─── Helpers réponses API ─────────────────────────────────────────────────────

def success_response(message: str, data: dict = None) -> dict:
    """Format standard de réponse succès."""
    response = {"success": True, "message": message}
    if data:
        response["data"] = data
    return response


def error_response(message: str, errors: dict = None) -> dict:
    """Format standard de réponse erreur."""
    response = {"success": False, "message": message}
    if errors:
        response["errors"] = errors
    return response