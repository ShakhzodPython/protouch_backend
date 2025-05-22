from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Carousel, CarouselDiscount
from .serializers import CarouselSerializer, CarouselDiscountSerializer


# Create your views here.


class ListCarouselAPIView(APIView):
    def get(self, request):
        """Retrieve all carousels"""
        carousels = Carousel.objects.all()
        serializer = CarouselSerializer(
            carousels, many=True, context={"request": request}
        )
        return Response(
            status=status.HTTP_200_OK,
            data=serializer.data,
        )


class ListCarouselDiscountAPIView(APIView):
    def get(self, request):
        """Retrieve all carousel discounts"""
        carousel_discounts = CarouselDiscount.objects.all()
        serializer = CarouselDiscountSerializer(
            carousel_discounts, many=True, context={"request": request}
        )
        return Response(
            status=status.HTTP_200_OK,
            data=serializer.data,
        )
