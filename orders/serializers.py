from rest_framework import serializers

from products.models import Product, ProductDiscount


class OrderItemSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(default=0)

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value


class OrderAddressSerializer(serializers.Serializer):
    country = serializers.CharField()
    address = serializers.CharField()
    floor = serializers.CharField()
    apartment = serializers.CharField()
    intercom_code = serializers.CharField(required=False)
    phone_number = serializers.CharField()


class CreateOrderSerializer(serializers.Serializer):
    customer_id = serializers.UUIDField()
    products = OrderItemSerializer(many=True, write_only=True)
    order_address = OrderAddressSerializer(write_only=True)
    order_payment = serializers.ChoiceField(
        choices=[
            ("PAYME", "PAYME"),
            ("CLICK", "CLICK"),
            ("UZUM", "UZUM"),
            ("CASH", "CASH"),
        ]
    )
    order_delivery = serializers.ChoiceField(
        choices=[("DELIVERY", "DELIVERY"), ("PICKUP", "PICKUP")]
    )

    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )


class UserOrderItemSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    title = serializers.CharField(source="product_id.title", read_only=True)
    price = serializers.DecimalField(
        source="product_id.price", max_digits=10, decimal_places=2, read_only=True
    )
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        image_obj = obj.product_id.product_images.first()
        if image_obj and image_obj.image:
            request = self.context.get("request")
            return (
                request.build_absolute_uri(image_obj.image.url)
                if request
                else image_obj.image.url
            )
        return None


class GetUserOrderSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    products = UserOrderItemSerializer(source="order_items", many=True)
    created_at = serializers.DateTimeField()
