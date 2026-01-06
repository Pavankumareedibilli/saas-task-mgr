from django.shortcuts import render
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .serializers import RegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
from .models import PasswordResetToken
from .password_reset_serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)

User = get_user_model()

class RegisterAPIView(generics.CreateAPIView):
    """
    POST /api/accounts/register/   -> create user
    """
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    POST /api/token/ -> returns access + refresh tokens using CustomTokenObtainPairSerializer
    Accepts 'username' field which may be username OR email.
    """
    serializer_class = CustomTokenObtainPairSerializer


class AccountViewSet(viewsets.GenericViewSet,
                     generics.RetrieveAPIView,
                     generics.UpdateAPIView):
    """
    Minimal viewset for handling logged-in user's profile. Routes:
    - GET /api/accounts/me/    -> retrieve own profile
    - PATCH /api/accounts/me/  -> partial update
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        # always return current user for these endpoints
        return self.request.user

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Alternate explicit /me/ endpoint route if you prefer."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    

class PasswordResetRequestAPIView(APIView):
    """
    POST /api/auth/password-reset/request/
    """
    permission_classes = []

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        # If user exists, create token & send email
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Always return success
            return Response({"detail": "If the email exists, a reset link has been sent."})

        token_obj = PasswordResetToken.objects.create(user=user)

        reset_link = f"http://localhost:3000/reset-password?token={token_obj.token}"

        send_mail(
            subject="Password Reset",
            message=f"Use this link to reset your password:\n{reset_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return Response({"detail": "If the email exists, a reset link has been sent."})
    
class PasswordResetConfirmAPIView(APIView):
    """
    POST /api/auth/password-reset/confirm/
    """
    permission_classes = []

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_obj = serializer.validated_data["token_obj"]
        new_password = serializer.validated_data["new_password"]

        user = token_obj.user
        user.set_password(new_password)
        user.save()

        token_obj.is_used = True
        token_obj.save()

        return Response({"detail": "Password reset successful."})