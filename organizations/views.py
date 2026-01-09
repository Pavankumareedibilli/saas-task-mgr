from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Organization
from .serializers import OrganizationSerializer, OrganizationCreateSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings

from .models import Organization, OrganizationInvitation, OrganizationMembership
from .permissions import require_org_role
from .invitation_serializers import (
    OrganizationInviteSerializer,
    OrganizationInvitationAcceptSerializer,
)



class OrganizationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only organizations where user is a member
        return Organization.objects.filter(
            memberships__user=self.request.user,
            memberships__is_active=True
        ).distinct()

    def get_serializer_class(self):
        if self.action == "create":
            return OrganizationCreateSerializer
        return OrganizationSerializer

    def perform_create(self, serializer):
        serializer.save()

class OrganizationInviteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, org_id):
        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response({"detail": "Organization not found."}, status=404)

        # Only OWNER / ADMIN can invite
        require_org_role(
            request.user,
            organization,
            [OrganizationMembership.OWNER, OrganizationMembership.ADMIN],
        )

        serializer = OrganizationInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        role = serializer.validated_data["role"]

        # Prevent inviting existing member
        if OrganizationMembership.objects.filter(
            organization=organization,
            user__email=email,
            is_active=True,
        ).exists():
            return Response({"detail": "User already a member."}, status=400)

        invite, created = OrganizationInvitation.objects.get_or_create(
            organization=organization,
            email=email,
            defaults={
                "role": role,
                "invited_by": request.user,
            },
        )

        if not created:
            return Response({"detail": "Invitation already sent."}, status=400)

        invite_link = f"http://localhost:3000/accept-invite?token={invite.token}"

        send_mail(
            subject="Organization Invitation",
            message=f"You were invited to join {organization.name}.\n{invite_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return Response({"detail": "Invitation sent."}, status=201)


class OrganizationAcceptInviteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = OrganizationInvitationAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invite = serializer.validated_data["invite"]

        # Prevent accepting invite for different email
        if request.user.email != invite.email:
            return Response(
                {"detail": "This invitation was not sent to your email."},
                status=403,
            )

        # Create membership
        OrganizationMembership.objects.create(
            user=request.user,
            organization=invite.organization,
            role=invite.role,
        )

        invite.is_accepted = True
        invite.save()

        return Response({"detail": "Invitation accepted."})
