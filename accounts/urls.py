# accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterAPIView, CustomTokenObtainPairView, AccountViewSet
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
# register routes for the account viewset (we will only use 'me' and update)
router.register(r"accounts", AccountViewSet, basename="account")

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="account-register"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
]
