from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def initials(employee):
    """Returns employee initials, e.g. 'JD' for John Doe."""
    first = employee.first_name[:1] if employee.first_name else ""
    last = employee.last_name[:1] if employee.last_name else ""
    return f"{first}{last}"


@register.filter
def late_badge(attendance):
    """Returns the late minutes badge text, e.g. 'Retard (15m)' or 'À l\\'heure'."""
    if attendance.late_minutes > 0:
        return f"Retard ({attendance.late_minutes}m)"
    return ""


@register.filter
def dept_name(employee):
    """Returns department name safely."""
    if employee.department:
        return employee.department.name
    return "Non affecté"


@register.filter
def qr_expiry_text(qr):
    """Returns expiry status text for a QR code."""
    if qr.is_expired:
        return ""
    local_time = timezone.localtime(qr.expires_at)
    return f"Valide jusqu'à {local_time.strftime('%H:%M')}"


@register.filter
def time_fmt(dt, fmt="H:i"):
    """Format a datetime safely."""
    if dt is None:
        return "--"
    if fmt == "H:i":
        local = timezone.localtime(dt)
        return local.strftime("%H:%M")
    return str(dt)
