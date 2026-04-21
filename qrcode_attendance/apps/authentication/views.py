from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import LoginSerializer
from apps.employees.serializers import EmployeeDetailSerializer



class RegisterView(APIView):
    """
    POST /api/auth/register/
    Crée un nouvel employé (public ou admin selon config)
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmployeeDetailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Facultatif : on peut retourner le token directement après register
        refresh = RefreshToken.for_user(user)
        access  = refresh.access_token

        return Response({
            "message": "Compte créé avec succès.",
            "access":  str(access),
            "refresh": str(refresh),
            "user": serializer.data
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    POST /api/auth/login/
    Retourne access + refresh token + infos user
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        # Génération des tokens JWT
        refresh = RefreshToken.for_user(user)
        access  = refresh.access_token

        return Response({
            "access":  str(access),
            "refresh": str(refresh),
            "user": {
                "id":         user.id,
                "email":      user.email,
                "full_name":  user.full_name,
                "role":       user.role,
                "department": user.department.name if user.department else None,
            }
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Blackliste le refresh token → invalide la session
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "Le refresh token est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Déconnexion réussie."},
                status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {"detail": "Token invalide ou déjà blacklisté."},
                status=status.HTTP_400_BAD_REQUEST
            )


class RefreshView(APIView):
    """
    POST /api/auth/refresh/
    Retourne un nouvel access token depuis le refresh token
    """
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "Le refresh token est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                "access":  str(refresh.access_token),
                "refresh": str(refresh),   # Nouveau refresh (rotation activée)
            }, status=status.HTTP_200_OK)
        except TokenError:
            return Response(
                {"detail": "Refresh token invalide ou expiré."},
                status=status.HTTP_401_UNAUTHORIZED
            )


class MeView(APIView):
    """
    GET /api/auth/me/
    Retourne les infos de l'utilisateur connecté
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id":         user.id,
            "email":      user.email,
            "full_name":  user.full_name,
            "first_name": user.first_name,
            "last_name":  user.last_name,
            "role":       user.role,
            "department": user.department.name if user.department else None,
            "is_active":  user.is_active,
            "created_at": user.created_at,
        })