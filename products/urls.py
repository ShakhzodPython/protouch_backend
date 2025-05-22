from django.urls import path

from .views import ListCategoryAPIView, ListProductAPIView, ProductDetailAPIView

urlpatterns = [
    path("categories/", ListCategoryAPIView.as_view(), name="category_list"),
    path("", ListProductAPIView.as_view(), name="product_list"),
    path(
        "product/<uuid:product_id>/",
        ProductDetailAPIView.as_view(),
        name="product_detail",
    ),
]
