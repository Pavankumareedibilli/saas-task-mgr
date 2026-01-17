# projects/urls.py
from rest_framework.routers import DefaultRouter,path
from .views import BoardViewSet, ListViewSet, CardViewSet
from .views import (
    ListReorderAPIView,
    CardReorderAPIView,
    CardMoveAPIView,
)
from .views import BoardDetailAPIView


router = DefaultRouter()
router.register(r"boards", BoardViewSet, basename="board")
router.register(r"lists", ListViewSet, basename="list")
router.register(r"cards", CardViewSet, basename="card")

urlpatterns = router.urls


urlpatterns += [
    path("lists/<int:list_id>/reorder/", ListReorderAPIView.as_view()),
    path("cards/<int:card_id>/reorder/", CardReorderAPIView.as_view()),
    path("cards/<int:card_id>/move/", CardMoveAPIView.as_view()),
     path("boards/<int:board_id>/detail/", BoardDetailAPIView.as_view()),
]

