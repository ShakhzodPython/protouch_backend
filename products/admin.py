from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from .models import (
    Category,
    Product,
    ProductDetail,
    ProductDiscount,
    ProductImage,
    Brand,
)


# Register your models here.
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "created_at"]


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    list_display = [
        "tree_actions",
        "indented_title",
        "is_carousel",
        "parent",
        "created_at",
    ]
    search_fields = ("title",)
    mptt_level_indent = 20


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 4


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "price",
        "is_in_stock",
        "is_pre_order",
        "created_at",
    ]
    search_fields = ("title",)
    list_filter = ["is_in_stock", "is_pre_order", "created_at"]
    inlines = [ProductImageInline]


@admin.register(ProductDetail)
class ProductDetailAdmin(admin.ModelAdmin):
    list_display = ["id", "product_id", "key", "value", "created_at"]
    list_filter = ["created_at"]


@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "product",
        "percent",
        "start_date",
        "end_date",
        "is_active",
    ]
    list_filter = [
        "start_date",
        "end_date",
    ]

    def is_active(self, obj):
        return obj.is_active()

    is_active.boolean = True
