from decimal import Decimal

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db import transaction

from products.models import Product
from users.models import Customer
from .models import OrderAddress, OrderPayment, Order, OrderItem, OrderDelivery
from .serializers import CreateOrderSerializer, GetUserOrderSerializer


# Create your views here.


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            customer_id = validated_data["customer_id"]
            address = validated_data["order_address"]
            payment = validated_data["order_payment"]
            delivery_type = validated_data["order_delivery"]
            products = validated_data["products"]

            try:
                with transaction.atomic():
                    customer = Customer.objects.filter(id=customer_id).first()

                    # Create order address
                    order_address = OrderAddress.objects.create(**address)

                    # Create order payment & delivery type
                    order_payment, _ = OrderPayment.objects.get_or_create(type=payment)
                    order_delivery_type, _ = OrderDelivery.objects.get_or_create(
                        type=delivery_type
                    )

                    # Create order
                    order = Order.objects.create(
                        customer_id=customer,
                        order_address_id=order_address,
                        order_payment=order_payment,
                        order_delivery=order_delivery_type,
                    )

                    total_price = Decimal("0.00")

                    for item in products:
                        product = Product.objects.filter(id=item["product_id"]).first()
                        quantity = item["quantity"]

                        # Apply discount, if it is active
                        if (
                            hasattr(product, "discount")
                            and product.discount.is_active()
                        ):
                            price = product.discounted_price()
                        else:
                            price = product.price

                        # Create order items
                        OrderItem.objects.create(
                            order_id=order, product_id=product, quantity=quantity
                        )

                        total_price += price * quantity

                    order.total_price = total_price
                    order.save()

                    return Response(
                        status=status.HTTP_201_CREATED,
                        data={
                            "order_number": order.order_number,
                            "customer_id": str(customer_id),
                            "total_price": str(total_price),
                        },
                    )
            except Exception as e:
                return Response(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    data={"detail": str(e)},
                )
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class GetUserOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer = request.user
        orders = Order.objects.filter(customer_id=customer).prefetch_related(
            "order_items"
        )

        if orders is None:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"detail": "Orders not found"}
            )

        serializer = GetUserOrderSerializer(
            orders, many=True, context={"request": request}
        )
        return Response(status=status.HTTP_200_OK, data=serializer.data)
