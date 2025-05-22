from django.contrib import admin

from .models import File, CarouselColor, Carousel, CarouselDiscount

# Register your models here.


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ["id", "file", "created_at"]
    list_filter = ["created_at"]


@admin.register(CarouselColor)
class CarouselColorAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "background_color",
        "percentage_color",
        "button_background_color",
        "created_at",
    ]
    list_filter = ["created_at"]


@admin.register(Carousel)
class CarouselAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "url",
        "percentage",
        "carousel_color_id",
        "created_at",
    ]
    list_filter = ["created_at"]


@admin.register(CarouselDiscount)
class CarouselDiscountAdmin(admin.ModelAdmin):
    list_display = ["id", "url", "created_at"]
    list_filter = ["created_at"]