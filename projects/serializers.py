# projects/serializers.py
from rest_framework import serializers
from .models import Board, List, Card


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ("id", "name", "created_at")


class ListSerializer(serializers.ModelSerializer):
    position = serializers.FloatField(read_only=True)
    class Meta:
        model = List
        fields = ("id", "title", "position", "created_at")


class CardSerializer(serializers.ModelSerializer):
    position = serializers.FloatField(read_only=True)
    class Meta:
        model = Card
        fields = (
            "id",
            "title",
            "description",
            "position",
            "created_at",
        )
