from rest_framework import serializers
from django.contrib.auth import authenticate
from apps.employees.models import Employee


class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, data):
        email    = data.get("email")
        password = data.get("password")

        # Authentification Django standard
        user = authenticate(
            request=self.context.get("request"),
            username=email,      # USERNAME_FIELD = email
            password=password
        )

        if not user:
            raise serializers.ValidationError(
                "Email ou mot de passe incorrect."
            )
        if not user.is_active:
            raise serializers.ValidationError(
                "Ce compte est désactivé."
            )

        data["user"] = user
        return data


class TokenResponseSerializer(serializers.Serializer):
    """Serializer pour la réponse de login (lecture seule)."""
    access  = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user    = serializers.SerializerMethodField()

    def get_user(self, obj):
        user = obj["user"]
        return {
            "id":         user.id,
            "email":      user.email,
            "full_name":  user.full_name,
            "role":       user.role,
            "department": user.department.name if user.department else None,
        }