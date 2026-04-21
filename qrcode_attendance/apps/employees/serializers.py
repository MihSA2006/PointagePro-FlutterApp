from rest_framework import serializers
from .models import Employee, Department


# ─── Department ───────────────────────────────────────────────────────────────

class DepartmentSerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model  = Department
        fields = ["id", "name", "employee_count"]

    def get_employee_count(self, obj):
        return obj.employees.filter(is_active=True).count()


# ─── Employee ─────────────────────────────────────────────────────────────────

class EmployeeListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes."""
    department_name = serializers.CharField(
        source="department.name",
        read_only=True
    )

    class Meta:
        model  = Employee
        fields = [
            "id", "first_name", "last_name", "email",
            "department", "department_name",
            "role", "is_active", "created_at"
        ]
        read_only_fields = ["id", "created_at"]


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Serializer complet pour création / modification."""
    department_name = serializers.CharField(
        source="department.name",
        read_only=True
    )
    full_name = serializers.CharField(read_only=True)
    password  = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
        style={"input_type": "password"}
    )

    class Meta:
        model  = Employee
        fields = [
            "id", "first_name", "last_name", "full_name",
            "email", "password",
            "department", "department_name",
            "role", "is_active", "created_at"
        ]
        read_only_fields = ["id", "created_at", "full_name"]

    # ── Validation email unique ──
    def validate_email(self, value):
        qs = Employee.objects.filter(email=value)
        # Exclure l'instance courante en cas de mise à jour
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Un employé avec cet email existe déjà."
            )
        return value

    # ── Validation rôle ──
    def validate_role(self, value):
        allowed = [Employee.Role.ADMIN, Employee.Role.EMPLOYEE]
        if value not in allowed:
            raise serializers.ValidationError(
                f"Rôle invalide. Choisir parmi : {allowed}"
            )
        return value

    # ── Création avec mot de passe hashé ──
    def create(self, validated_data):
        password = validated_data.pop("password", None)
        employee = Employee(**validated_data)
        if password:
            employee.set_password(password)
        else:
            raise serializers.ValidationError(
                {"password": "Le mot de passe est obligatoire à la création."}
            )
        employee.save()
        return employee

    # ── Mise à jour avec mot de passe optionnel ──
    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance