from django.urls import path

from .views import ListCarouselAPIView, ListCarouselDiscountAPIView

urlpatterns = [
    path(
        "carousels/",
        ListCarouselAPIView.as_view(),
        name="carousel_list",
    ),
    path(
        "carousels/discount",
        ListCarouselDiscountAPIView.as_view(),
        name="carousel_discount_list",
    ),
]
