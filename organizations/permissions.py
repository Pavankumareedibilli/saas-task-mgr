# organizations/permissions.py
from rest_framework.exceptions import PermissionDenied
from .models import OrganizationMembership


def require_org_role(user, organization, allowed_roles):
    """
    Ensure user has one of the allowed roles in the organization.
    """
    membership = OrganizationMembership.objects.filter(
        user=user,
        organization=organization,
        is_active=True
    ).first()

    if not membership or membership.role not in allowed_roles:
        raise PermissionDenied("You do not have permission to perform this action.")

    return membership
