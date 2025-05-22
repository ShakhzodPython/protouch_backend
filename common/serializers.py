from rest_framework import serializers

from .models import File, CarouselColor, Carousel, CarouselDiscount


class FileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(source="file", read_only=True)

    class Meta:
        model = File
        fields = ["id", "url"]

    def get_url(self, obj):
        request = self.context.get("request")
        if obj.file:
            return request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return None


class CarouselColorSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    background_color = serializers.CharField()
    percentage_color = serializers.CharField()
    button_background_color = serializers.CharField()


class CarouselSerializer(serializers.ModelSerializer):
    carousel_color = CarouselColorSerializer(source="carousel_color_id", read_only=True)
    image = FileSerializer(source="image_id", read_only=True)

    class Meta:
        model = Carousel
        fields = [
            "id",
            "text",
            "percentage",
            "url",
            "carousel_color",
            "image",
        ]


class CarouselDiscountSerializer(serializers.ModelSerializer):
    image = FileSerializer(source="image_id", read_only=True)

    class Meta:
        model = CarouselDiscount
        fields = ["id", "url", "image"]