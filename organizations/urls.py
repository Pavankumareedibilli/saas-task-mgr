# organizations/urls.py
from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet
from django.urls import path
from .views import OrganizationInviteAPIView, OrganizationAcceptInviteAPIView

router = DefaultRouter()
router.register(r"organizations", OrganizationViewSet, basename="organization")

urlpatterns = router.urls

urlpatterns += [
    path("organizations/<int:org_id>/invite/", OrganizationInviteAPIView.as_view()),
    path("organizations/invitations/accept/", OrganizationAcceptInviteAPIView.as_view()),
]