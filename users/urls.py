from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import CreateCustomerAPIView, GetMeAPIView, UpdateCustomerAPIView

urlpatterns = [
    path("register/", CreateCustomerAPIView.as_view(), name="sign_up"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", GetMeAPIView.as_view(), name="get_me"),
    path("update/", UpdateCustomerAPIView.as_view(), name="update"),
]
