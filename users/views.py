import requests

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from django.db import transaction, IntegrityError

from .models import Customer
from .serializers import (
    CreateCustomerSerializer,
    GetMeSerializer,
    UpdateCustomerSerializer,
)


# Create your views here.
class CreateCustomerAPIView(CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CreateCustomerSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email_or_phone = request.data.get("email_or_phone")
        user = serializer.save()

        return Response(
            status=status.HTTP_201_CREATED,
            data={
                "id": str(user.id),
                "email_or_phone": (
                    user.phone_number if email_or_phone.isdigit() else user.email
                ),
            },
        )


class GoogleLoginAPIView(APIView):
    def post(self, request):
        token = request.data.get("token")
        if token is None:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={"detail": "Token is required"}
            )

        try:
            response = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status_code != 200:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"detail": "Invalid access token"},
                )

            user_data = response.json()
            email = user_data.get("email")
            first_name = user_data.get("name")

            customer = Customer.objects.filter(email=email).first()

            if customer is None:
                try:
                    with transaction.atomic():
                        customer = Customer.objects.create(
                            email=email, first_name=first_name
                        )
                except IntegrityError:
                    customer = Customer.objects.get(email=email)

            refresh_token = RefreshToken.for_user(customer)
            access_token = str(refresh_token.access_token)

            return Response(
                status=status.HTTP_200_OK,
                data={
                    "access_token": access_token,
                    "refresh_token": str(refresh_token),
                    "customer": {
                        "id": customer.id,
                        "email": customer.email,
                        "first_name": first_name,
                    },
                },
            )
        except Exception as e:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"detail": f"Invalid token: {str(e)}"},
            )


class GetMeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = GetMeSerializer(request.user)
        return Response(serializer.data)


class UpdateCustomerAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        customer = request.user
        serializer = UpdateCustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    def patch(self, request, *args, **kwargs):
        customer = request.user
        serializer = UpdateCustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
