from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


# ─── Department ───────────────────────────────────────────────────────────────
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "departments"
        verbose_name = "Département"
        verbose_name_plural = "Départements"
        ordering = ["name"]

    def __str__(self):
        return self.name


# ─── Employee Manager ─────────────────────────────────────────────────────────
class EmployeeManager(BaseUserManager):
    """
    Manager custom pour créer des employés/admins
    sans champ 'username' (on utilise email)
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        extra_fields.setdefault("role", Employee.Role.EMPLOYEE)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", Employee.Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


# ─── Employee ─────────────────────────────────────────────────────────────────
class Employee(AbstractBaseUser, PermissionsMixin):
    """
    Modèle utilisateur principal.
    Remplace complètement le User Django par défaut.
    L'email sert d'identifiant unique (pas de username).
    """

    class Role(models.TextChoices):
        ADMIN    = "admin",    "Administrateur"
        EMPLOYEE = "employee", "Employé"

    # ── Champs identité ──
    first_name  = models.CharField(max_length=100)
    last_name   = models.CharField(max_length=100)
    email       = models.EmailField(unique=True)

    # ── Organisation ──
    department  = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees"
    )

    # ── Rôle & statut ──
    role        = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.EMPLOYEE
    )
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)  # Accès admin Django

    # ── Timestamps ──
    created_at  = models.DateTimeField(default=timezone.now)

    # ── Auth config ──
    USERNAME_FIELD  = "email"          # Login par email
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = EmployeeManager()

    class Meta:
        db_table = "employees"
        verbose_name = "Employé"
        verbose_name_plural = "Employés"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    # ── Propriétés utiles ──
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN