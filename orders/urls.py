from django.urls import path

from .views import CreateOrderAPIView, GetUserOrderAPIView

urlpatterns = [
    path("", GetUserOrderAPIView.as_view(), name="orders"),
    path("create/", CreateOrderAPIView.as_view(), name=""),
]
