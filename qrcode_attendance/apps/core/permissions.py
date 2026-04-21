from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminRole(BasePermission):
    """Accès uniquement aux utilisateurs role='admin'."""
    message = "Accès réservé aux administrateurs."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsEmployeeRole(BasePermission):
    """Accès aux employés ET admins authentifiés."""
    message = "Accès réservé aux employés authentifiés."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ["admin", "employee"]
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Niveau objet :
    - Admin → accès total
    - Employee → seulement ses propres objets
    """
    message = "Vous n'avez pas accès à cette ressource."

    def has_object_permission(self, request, view, obj):
        if request.user.role == "admin":
            return True
        employee = getattr(obj, "employee", None)
        return employee == request.user


class IsAdminOrReadOnly(BasePermission):
    """
    Admin → lecture + écriture
    Employee → lecture seule (GET, HEAD, OPTIONS)
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == "admin"