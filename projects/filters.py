
import django_filters
from .models import Card


class CardFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    board_id = django_filters.NumberFilter(field_name="list__board_id")
    list_id = django_filters.NumberFilter(field_name="list_id")
    is_archived = django_filters.BooleanFilter()

    class Meta:
        model = Card
        fields = ["title", "board_id", "list_id", "is_archived"]
