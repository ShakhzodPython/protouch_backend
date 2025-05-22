from django.utils import translation
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from .models import Category, Product
from .filters import ProductFilter
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductRetrieveSerializer as ProductDetailSerializer,
)


# Create your views here.


class ListCategoryAPIView(APIView):
    def get(self, request):
        is_carousel = request.query_params.get("is_carousel")
        lang = self.request.query_params.get("lang", None)

        if lang in ["ru", "uz", "en"]:
            translation.activate(lang)

        categories = Category.objects.filter(parent__isnull=True)

        if is_carousel:
            if is_carousel.lower() == "true":
                categories = categories.filter(is_carousel=True)
            elif is_carousel.lower() == "false":
                categories = categories.filter(is_carousel=False)
            else:
                categories = []

        serializer = CategorySerializer(
            categories, many=True, context={"request": request}
        )
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ListProductAPIView(ListAPIView):
    queryset = Product.objects.all().order_by("id").distinct()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    pagination_class = PageNumberPagination

    def get_paginated_response(self, data):
        return self.paginator.get_paginated_response(data)


class ProductDetailAPIView(APIView):
    def get(self, request, product_id):
        lang = self.request.query_params.get("lang", None)

        if lang in ["ru", "uz", "en"]:
            translation.activate(lang)

        product = Product.objects.filter(id=product_id).first()
        if product is None:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"detail": "Product not found"}
            )
        serializer = ProductDetailSerializer(product, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)
