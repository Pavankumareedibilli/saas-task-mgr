from django.shortcuts import render

# Create your views here.
# projects/views.py
from rest_framework import viewsets, permissions
from organizations.models import OrganizationMembership, Organization
from organizations.permissions import require_org_role
from .models import Board
from .serializers import BoardSerializer
from .models import List
from .serializers import ListSerializer
from .models import Card
from .serializers import CardSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from .utils import calculate_position


class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Board.objects.filter(
            organization__memberships__user=self.request.user,
            organization__memberships__is_active=True,
        ).distinct()

    def perform_create(self, serializer):
        org_id = self.request.data.get("organization_id")
        if not org_id:
            raise ValueError("organization_id is required")

        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            raise ValueError("Invalid organization")

        require_org_role(
            self.request.user,
            organization,
            [
                OrganizationMembership.OWNER,
                OrganizationMembership.ADMIN,
                OrganizationMembership.MEMBER,
            ],
        )

        serializer.save(
            organization=organization,
            created_by=self.request.user,
        )

class ListViewSet(viewsets.ModelViewSet):
    serializer_class = ListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return List.objects.filter(
            board__organization__memberships__user=self.request.user,
            board__organization__memberships__is_active=True,
        ).distinct()

    def perform_create(self, serializer):
        board_id = self.request.data.get("board_id")
        if not board_id:
            raise ValueError("board_id is required")

        board = Board.objects.get(id=board_id)

        require_org_role(
            self.request.user,
            board.organization,
            [
                OrganizationMembership.OWNER,
                OrganizationMembership.ADMIN,
                OrganizationMembership.MEMBER,
            ],
        )

        # position logic: append to end
        last = List.objects.filter(board=board).order_by("-position").first()
        position = (last.position + 1) if last else 1.0

        serializer.save(board=board, position=position)

class CardViewSet(viewsets.ModelViewSet):
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Card.objects.filter(
            list__board__organization__memberships__user=self.request.user,
            list__board__organization__memberships__is_active=True,
        ).distinct()

    def perform_create(self, serializer):
        list_id = self.request.data.get("list_id")
        if not list_id:
            raise ValueError("list_id is required")

        list_obj = List.objects.get(id=list_id)

        require_org_role(
            self.request.user,
            list_obj.board.organization,
            [
                OrganizationMembership.OWNER,
                OrganizationMembership.ADMIN,
                OrganizationMembership.MEMBER,
            ],
        )

        last = Card.objects.filter(list=list_obj).order_by("-position").first()
        position = (last.position + 1) if last else 1.0

        serializer.save(
            list=list_obj,
            position=position,
            created_by=self.request.user,
        )

class ListReorderAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def patch(self, request, list_id):
        try:
            list_obj = List.objects.select_for_update().get(id=list_id)
        except List.DoesNotExist:
            return Response({"detail": "List not found."}, status=404)

        # tenant & role check
        require_org_role(
            request.user,
            list_obj.board.organization,
            [
                OrganizationMembership.OWNER,
                OrganizationMembership.ADMIN,
                OrganizationMembership.MEMBER,
            ],
        )

        before_id = request.data.get("before_id")
        after_id = request.data.get("after_id")

        before = (
            List.objects.get(id=before_id).position
            if before_id else None
        )
        after = (
            List.objects.get(id=after_id).position
            if after_id else None
        )

        list_obj.position = calculate_position(before, after)
        list_obj.save()

        return Response({"detail": "List reordered."})

class CardReorderAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def patch(self, request, card_id):
        try:
            card = Card.objects.select_for_update().get(id=card_id)
        except Card.DoesNotExist:
            return Response({"detail": "Card not found."}, status=404)

        require_org_role(
            request.user,
            card.list.board.organization,
            [
                OrganizationMembership.OWNER,
                OrganizationMembership.ADMIN,
                OrganizationMembership.MEMBER,
            ],
        )

        before_id = request.data.get("before_id")
        after_id = request.data.get("after_id")

        before = (
            Card.objects.get(id=before_id).position
            if before_id else None
        )
        after = (
            Card.objects.get(id=after_id).position
            if after_id else None
        )

        card.position = calculate_position(before, after)
        card.save()

        return Response({"detail": "Card reordered."})

class CardMoveAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def patch(self, request, card_id):
        try:
            card = Card.objects.select_for_update().get(id=card_id)
        except Card.DoesNotExist:
            return Response({"detail": "Card not found."}, status=404)

        target_list_id = request.data.get("target_list_id")
        if not target_list_id:
            return Response({"detail": "target_list_id required."}, status=400)

        try:
            target_list = List.objects.select_for_update().get(id=target_list_id)
        except List.DoesNotExist:
            return Response({"detail": "Target list not found."}, status=404)

        # Ensure same organization (no cross-tenant move)
        if card.list.board.organization_id != target_list.board.organization_id:
            return Response({"detail": "Cross-organization move not allowed."}, status=403)

        require_org_role(
            request.user,
            card.list.board.organization,
            [
                OrganizationMembership.OWNER,
                OrganizationMembership.ADMIN,
                OrganizationMembership.MEMBER,
            ],
        )

        before_id = request.data.get("before_id")
        after_id = request.data.get("after_id")

        before = (
            Card.objects.get(id=before_id).position
            if before_id else None
        )
        after = (
            Card.objects.get(id=after_id).position
            if after_id else None
        )

        card.list = target_list
        card.position = calculate_position(before, after)
        card.save()

        return Response({"detail": "Card moved."})
