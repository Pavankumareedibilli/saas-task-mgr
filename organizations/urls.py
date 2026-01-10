# organizations/urls.py
from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet
from django.urls import path
from .views import OrganizationInviteAPIView, OrganizationAcceptInviteAPIView
from .views import (
    OrganizationMembersAPIView,
    OrganizationMemberRoleUpdateAPIView,
    OrganizationMemberRemoveAPIView,
)

router = DefaultRouter()
router.register(r"organizations", OrganizationViewSet, basename="organization")

urlpatterns = router.urls

urlpatterns += [
    path("organizations/<int:org_id>/invite/", OrganizationInviteAPIView.as_view()),
    path("organizations/invitations/accept/", OrganizationAcceptInviteAPIView.as_view()),
    path("organizations/<int:org_id>/members/", OrganizationMembersAPIView.as_view()),
    path(
        "organizations/<int:org_id>/members/<int:member_id>/role/",
        OrganizationMemberRoleUpdateAPIView.as_view(),
    ),
    path(
        "organizations/<int:org_id>/members/<int:member_id>/remove/",
        OrganizationMemberRemoveAPIView.as_view(),
    ),
]