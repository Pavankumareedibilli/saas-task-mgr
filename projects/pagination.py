
from rest_framework.pagination import CursorPagination


class CardCursorPagination(CursorPagination):
    page_size = 20
    ordering = "-created_at"  
