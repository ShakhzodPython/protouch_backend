from django.contrib import admin

from orders.models import (
    OrderAddress,
    OrderPayment,
    OrderDelivery,
    Order,
    OrderItem,
)


# Register your models here.


@admin.register(OrderAddress)
class OrderAddressAdmin(admin.ModelAdmin):
    list_display = ["id", "country", "address", "apartment", "phone_number"]
    list_filter = ["created_at"]


@admin.register(OrderPayment)
class OrderPaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "type", "created_at"]
    list_filter = ["created_at"]


@admin.register(OrderDelivery)
class OrderDeliveryAdmin(admin.ModelAdmin):
    list_display = ["id", "type", "created_at"]
    list_filter = ["created_at"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer_id", "total_price", "created_at"]
    search_fields = ["id", "customer_id__first_name", "customer_id__last_name"]
    list_filter = ["created_at"]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["id", "order_id", "product_id", "created_at"]
    search_fields = ["order_id", "product_id"]
    list_filter = ["created_at"]
