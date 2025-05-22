from rest_framework import serializers


from common.serializers import FileSerializer
from .models import (
    Category,
    ProductImage,
    ProductDetail,
    ProductDiscount,
    Product,
    Brand,
)


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "title"]


class CategoryChildrenSerializer(serializers.ModelSerializer):
    brands = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "title", "slug", "brands"]

    def get_brands(self, obj):
        if obj.parent is not None:
            return BrandSerializer(obj.brands.all(), many=True).data
        return None


class CategorySerializer(serializers.ModelSerializer):
    image = FileSerializer(source="image_id", read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "title",
            "slug",
            "is_carousel",
            "image",
            "children",
        ]

    def get_children(self, obj):
        children = obj.children.all()
        return CategoryChildrenSerializer(children, many=True).data


class ProductImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["id", "url"]

    def get_url(self, obj):
        request = self.context.get("request")
        if obj.image:
            return (
                request.build_absolute_uri(obj.image.url) if request else obj.image.url
            )
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDetail
        fields = ["id", "key", "value"]


class ProductDiscountSerializer(serializers.ModelSerializer):
    discounted_price = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = ProductDiscount
        fields = [
            "id",
            "percent",
            "discounted_price",
            "start_date",
            "end_date",
            "is_active",
        ]

    def get_discounted_price(self, obj):
        return obj.discounted_price()

    def get_is_active(self, obj):
        return obj.is_active()


class ProductSerializer(serializers.ModelSerializer):
    discount = ProductDiscountSerializer()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "short_description",
            "slug",
            "price",
            "is_in_stock",
            "is_pre_order",
            "image",
            "discount",
        ]

    def get_image(self, obj):
        image_obj = obj.product_images.first()
        if image_obj and image_obj.image:
            request = self.context.get("request")
            return (
                request.build_absolute_uri(image_obj.image.url)
                if request
                else image_obj.image.url
            )
        return None


class ProductRetrieveSerializer(serializers.ModelSerializer):
    discount = ProductDiscountSerializer()
    images = ProductImageSerializer(many=True, read_only=True, source="product_images")
    details = ProductDetailSerializer(many=True, source="product_details")

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "price",
            "short_description",
            "description",
            "is_in_stock",
            "is_pre_order",
            "discount",
            "images",
            "details",
        ]
