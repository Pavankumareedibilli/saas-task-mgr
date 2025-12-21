from django.shortcuts import render

# Create your views here.
# accounts/views.py
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .serializers import RegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

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
