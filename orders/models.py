from enum import Enum
from django.db import models

from products.models import Product
from utils.base import BaseModel
from users.models import Customer
from utils.validation import generate_order_number


# Create your models here.
class OrderAddress(BaseModel):
    country = models.CharField(max_length=55, verbose_name="Country")
    address = models.CharField(max_length=55, verbose_name="Address")
    floor = models.CharField(max_length=55, verbose_name="Floor")
    apartment = models.CharField(max_length=55, verbose_name="Apartment")
    intercom_code = models.CharField(max_length=55, verbose_name="Intercom code")
    phone_number = models.CharField(max_length=55, verbose_name="Phone number")

    class Meta:
        verbose_name = "Order Address"
        verbose_name_plural = "Order Addresses"


class OrderDeliveryType(Enum):
    DELIVERY = "DELIVERY"
    PICKUP = "PICKUP"

    @classmethod
    def choices(cls):
        # Return a list of tuples (enum: value)
        return [(tag.name, tag.value) for tag in cls]


class OrderDelivery(BaseModel):
    type = models.CharField(
        max_length=10,
        choices=OrderDeliveryType.choices(),
        default=OrderDeliveryType.DELIVERY.value,
    )

    class Meta:
        verbose_name = "Order Delivery"
        verbose_name_plural = "Order Deliveries"

    def __str__(self):
        return f"OrderDelivery : {self.type}"


class OrderPaymentType(Enum):
    PAYMNE = "PAYME"
    CLICK = "CLICK"
    UZUM = "UZUM"
    CASH = "CASH"

    @classmethod
    def choices(cls):
        # Return a list of tuples (enum: value)
        return [(tag.name, tag.value) for tag in cls]


class OrderPayment(BaseModel):
    type = models.CharField(
        max_length=10,
        choices=OrderPaymentType.choices(),
        default=OrderPaymentType.PAYMNE.value,
    )

    class Meta:
        verbose_name = "Order Payment"
        verbose_name_plural = "Order Payments"

    def __str__(self):
        return f"OrderPayment: {self.type}"


class Order(BaseModel):
    customer_id = models.ForeignKey(Customer, on_delete=models.PROTECT)
    order_number = models.CharField(
        max_length=6, unique=True, default=generate_order_number
    )
    order_address_id = models.ForeignKey(OrderAddress, on_delete=models.CASCADE)
    order_payment = models.ForeignKey(OrderPayment, on_delete=models.CASCADE)
    order_delivery = models.ForeignKey(OrderDelivery, on_delete=models.CASCADE)
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, editable=False
    )

    def __str__(self):
        return f"Customer ID: {self.customer_id} | Order number: {self.order_number} | Total price: {self.total_price}"


class OrderItem(BaseModel):
    order_id = models.ForeignKey(
        "Order", on_delete=models.CASCADE, related_name="order_items"
    )
    product_id = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=False, blank=False
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    @property
    def order_total(self):
        discount = getattr(self.product_id, "discount", None)
        if discount and discount.is_active():
            discounted_price = discount.discounted_price()
            total_price = self.quantity * discounted_price
        else:
            total_price = self.quantity * self.product_id.price
        return total_price

    def __str__(self):
        return f"Order ID: {self.order_id} | Product ID: {self.product_id} | Quantity: {self.quantity}"
