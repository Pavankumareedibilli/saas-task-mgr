# projects/urls.py
from rest_framework.routers import DefaultRouter,path
from .views import BoardViewSet, ListViewSet, CardViewSet
from .activity_views import ActivityLogListAPIView
from .views import (
    ListReorderAPIView,
    CardReorderAPIView,
    CardMoveAPIView,
    BoardArchiveAPIView,
    BoardRestoreAPIView,
    ListArchiveAPIView,
    ListRestoreAPIView,
    CardArchiveAPIView,
    CardRestoreAPIView,
    CardSearchAPIView,
    CardAssignAPIView,
)
from .views import BoardDetailAPIView
from .notification_views import (
    NotificationListAPIView,
    NotificationMarkReadAPIView,
)

router = DefaultRouter()
router.register(r"boards", BoardViewSet, basename="board")
router.register(r"lists", ListViewSet, basename="list")
router.register(r"cards", CardViewSet, basename="card")
router.register(r"card-search", CardSearchAPIView, basename="card-search")


urlpatterns = router.urls


urlpatterns += [
    path("lists/<int:list_id>/reorder/", ListReorderAPIView.as_view()),
    path("cards/<int:card_id>/reorder/", CardReorderAPIView.as_view()),
    path("cards/<int:card_id>/move/", CardMoveAPIView.as_view()),
    path("boards/<int:board_id>/detail/", BoardDetailAPIView.as_view()),
    path("boards/<int:board_id>/archive/", BoardArchiveAPIView.as_view()),
    path("boards/<int:board_id>/restore/", BoardRestoreAPIView.as_view()),

    path("lists/<int:list_id>/archive/", ListArchiveAPIView.as_view()),
    path("lists/<int:list_id>/restore/", ListRestoreAPIView.as_view()),

    path("cards/<int:card_id>/archive/", CardArchiveAPIView.as_view()),
    path("cards/<int:card_id>/restore/", CardRestoreAPIView.as_view()),
    path("activity-logs/", ActivityLogListAPIView.as_view()),
    path("notifications/", NotificationListAPIView.as_view()),
    path("notifications/<int:pk>/read/", NotificationMarkReadAPIView.as_view()),
    path("cards/<int:card_id>/assign/", CardAssignAPIView.as_view()),
    
]

