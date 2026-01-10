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
from .member_serializers import (
    OrganizationMemberSerializer,
    OrganizationMemberRoleUpdateSerializer,
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
    
class OrganizationMembersAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, org_id):
        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response({"detail": "Organization not found."}, status=404)

        # Any active member can list members
        require_org_role(
            request.user,
            organization,
            [
                OrganizationMembership.OWNER,
                OrganizationMembership.ADMIN,
                OrganizationMembership.MEMBER,
            ],
        )

        members = organization.memberships.select_related("user").filter(is_active=True)
        serializer = OrganizationMemberSerializer(members, many=True)
        return Response(serializer.data)

class OrganizationMemberRoleUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, org_id, member_id):
        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response({"detail": "Organization not found."}, status=404)

        # Only OWNER can change roles
        require_org_role(
            request.user,
            organization,
            [OrganizationMembership.OWNER],
        )

        try:
            membership = OrganizationMembership.objects.get(
                id=member_id,
                organization=organization,
                is_active=True,
            )
        except OrganizationMembership.DoesNotExist:
            return Response({"detail": "Member not found."}, status=404)

        serializer = OrganizationMemberRoleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Prevent owner demoting themselves (lockout protection)
        if (
            membership.user == request.user
            and membership.role == OrganizationMembership.OWNER
            and serializer.validated_data["role"] != OrganizationMembership.OWNER
        ):
            return Response(
                {"detail": "Owner cannot demote themselves."},
                status=400,
            )

        membership.role = serializer.validated_data["role"]
        membership.save()

        return Response({"detail": "Role updated."})

class OrganizationMemberRemoveAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, org_id, member_id):
        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response({"detail": "Organization not found."}, status=404)

        requester_membership = require_org_role(
            request.user,
            organization,
            [OrganizationMembership.OWNER, OrganizationMembership.ADMIN],
        )

        try:
            membership = OrganizationMembership.objects.get(
                id=member_id,
                organization=organization,
                is_active=True,
            )
        except OrganizationMembership.DoesNotExist:
            return Response({"detail": "Member not found."}, status=404)

        # Admin cannot remove OWNER
        if (
            requester_membership.role == OrganizationMembership.ADMIN
            and membership.role == OrganizationMembership.OWNER
        ):
            return Response(
                {"detail": "Admin cannot remove owner."},
                status=403,
            )

        # Prevent owner removing themselves
        if membership.user == request.user and membership.role == OrganizationMembership.OWNER:
            return Response(
                {"detail": "Owner cannot remove themselves."},
                status=400,
            )

        membership.is_active = False
        membership.save()

        return Response({"detail": "Member removed."})
