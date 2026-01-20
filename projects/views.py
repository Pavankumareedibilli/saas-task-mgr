from django.shortcuts import render
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
from django.db.models import Prefetch
from .serializers import BoardDetailSerializer
from .activity_logger import log_activity




class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Board.objects.filter(
            is_archived=False,
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
        board = serializer.save(
            organization=organization,
            created_by=self.request.user,
        )
        log_activity(
        organization=organization,
        actor=self.request.user,
        action="BOARD_CREATED",
        metadata={
            "board_id": board.id,
            "board_name": board.name,
        },
    )

class ListViewSet(viewsets.ModelViewSet):
    serializer_class = ListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return List.objects.filter(
            is_archived=False,
            board__is_archived=False,
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
            is_archived=False,
            list__is_archived=False,
            list__board__is_archived=False,
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
        card = serializer.save(
            list=list_obj,
            position=position,
            created_by=self.request.user,
        )
        log_activity(
            organization=list_obj.board.organization,
            actor=self.request.user,
            action="CARD_CREATED",
            metadata={
                "card_id": card.id,
                "list_id": list_obj.id,
                "title": card.title,
            },
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
        old_list_id = card.list_id
        card.list = target_list
        card.position = calculate_position(before, after)
        card.save()
        log_activity(
            organization=target_list.board.organization,
            actor=request.user,
            action="CARD_MOVED",
            metadata={
                "card_id": card.id,
                "from_list": old_list_id,
                "to_list": target_list.id,
            },
        )
        return Response({"detail": "Card moved."})
    

    

class BoardDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, board_id):
        try:
            board = (
                Board.objects
                .select_related("organization")
                .prefetch_related(
                    Prefetch(
                        "lists",
                        queryset=List.objects.filter(is_archived=False)
                        .order_by("position")
                        .prefetch_related(
                            Prefetch(
                                "cards",
                                queryset=Card.objects.filter(is_archived=False).order_by("position"),
                            )
                        ),
                    )
                )

                .get(
                    id=board_id,
                    organization__memberships__user=request.user,
                    organization__memberships__is_active=True,
                )
            )
        except Board.DoesNotExist:
            return Response({"detail": "Board not found."}, status=404)

        serializer = BoardDetailSerializer(board)
        return Response(serializer.data)

class BoardArchiveAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, board_id):
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return Response({"detail": "Board not found."}, status=404)

        require_org_role(
            request.user,
            board.organization,
            [
                OrganizationMembership.OWNER,
                OrganizationMembership.ADMIN,
            ],
        )

        board.is_archived = True
        board.save()

        return Response({"detail": "Board archived."})

class BoardRestoreAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, board_id):
        try:
            board = Board.objects.get(id=board_id, is_archived=True)
        except Board.DoesNotExist:
            return Response({"detail": "Archived board not found."}, status=404)

        require_org_role(
            request.user,
            board.organization,
            [
                OrganizationMembership.OWNER,
                OrganizationMembership.ADMIN,
            ],
        )

        board.is_archived = False
        board.save()

        return Response({"detail": "Board restored."})

class ListArchiveAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, list_id):
        list_obj = List.objects.get(id=list_id)

        require_org_role(
            request.user,
            list_obj.board.organization,
            [
                OrganizationMembership.OWNER,
                OrganizationMembership.ADMIN,
            ],
        )

        list_obj.is_archived = True
        list_obj.save()
        return Response({"detail": "List archived."})

class ListRestoreAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, list_id):
        list_obj = List.objects.get(id=list_id, is_archived=True)

        require_org_role(
            request.user,
            list_obj.board.organization,
            [
                OrganizationMembership.OWNER,
                OrganizationMembership.ADMIN,
            ],
        )

        list_obj.is_archived = False
        list_obj.save()
        return Response({"detail": "List restored."})
class CardArchiveAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, card_id):
        card = Card.objects.get(id=card_id)

        require_org_role(
            request.user,
            card.list.board.organization,
            [
                OrganizationMembership.OWNER,
                OrganizationMembership.ADMIN,
                OrganizationMembership.MEMBER,
            ],
        )

        card.is_archived = True
        card.save()
        log_activity(
            organization=card.list.board.organization,
            actor=request.user,
            action="CARD_ARCHIVED",
            metadata={
                "card_id": card.id,
                "title": card.title,
            },
        )
        return Response({"detail": "Card archived."})

class CardRestoreAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, card_id):
        card = Card.objects.get(id=card_id, is_archived=True)

        require_org_role(
            request.user,
            card.list.board.organization,
            [
                OrganizationMembership.OWNER,
                OrganizationMembership.ADMIN,
                OrganizationMembership.MEMBER,
            ],
        )

        card.is_archived = False
        card.save()
        return Response({"detail": "Card restored."})
