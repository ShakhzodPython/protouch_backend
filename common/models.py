import os

from PIL import Image
from io import BytesIO

from django.db import models
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

from core import settings
from utils.base import BaseModel


# Create your models here.
class File(BaseModel):
    file = models.FileField(
        upload_to="uploads/files",
        verbose_name="Files",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp"],
            )
        ],
    )

    class Meta:
        verbose_name = "File"
        verbose_name_plural = "Files"

    def __str__(self):
        element = r"""[\]"""
        return f"ID: {self.id} | Name: {self.file.name.split(element)[-1]}"

    def clean(self):
        file_extension = self.file.name.split(".")[-1].lower()
        if file_extension not in ["jpg", "jpeg", "png", "webp"]:
            raise ValidationError(
                f"File: {self.file.name.split('/')[-1]} is not a valid image format. Allow formats are JPG, JPEG, PNG, and WEBP"
            )

    def save(self, *args, **kwargs):
        is_webp = self.file.name.split(".")[-1].lower() == "webp"
        original_path = None

        if not is_webp and self.file:
            original_path = os.path.join(
                settings.MEDIA_ROOT + "/uploads/files/", self.file.name
            )

        super().save(*args, **kwargs)

        if not is_webp:
            image = Image.open(self.file)
            image = image.convert("RGBA")

            webp_io = BytesIO()
            image.save(webp_io, format="WEBP", quality=80)

            webp_path = os.path.splitext(os.path.basename(self.file.name))[0] + ".webp"
            self.file.save(webp_path, ContentFile(webp_io.getvalue()), save=False)
            super().save(*args, **kwargs)

            # Deleting original image
            if original_path and os.path.exists(original_path):
                os.remove(original_path)


class CarouselColor(BaseModel):
    background_color = models.CharField(max_length=55, verbose_name="Background color")
    percentage_color = models.CharField(max_length=55, verbose_name="Percentage color")
    button_background_color = models.CharField(
        max_length=55, verbose_name="Button background color"
    )

    class Meta:
        verbose_name = "Carousel Color"
        verbose_name_plural = "Carousel Colors"

    def __str__(self):
        return f"ID: {self.id} | Background color: {self.background_color} | Percentage color: {self.percentage_color} |\nButton background color: {self.button_background_color}"


class Carousel(BaseModel):
    text = models.CharField(max_length=255, verbose_name="Text")
    percentage = models.PositiveIntegerField(default=0, verbose_name="Percentage")
    url = models.URLField(verbose_name="Url")
    carousel_color_id = models.ForeignKey(
        CarouselColor, verbose_name="Carousel color", on_delete=models.PROTECT
    )
    image_id = models.ForeignKey(File, verbose_name="Image", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Carousel"
        verbose_name_plural = "Carousels"

    def __str__(self):
        return f"ID: {self.id} | Text: {self.text} | Percentage: {self.percentage}"


class CarouselDiscount(BaseModel):
    url = models.URLField(verbose_name="Url")
    image_id = models.ForeignKey(File, verbose_name="Image", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Carousel Discount"
        verbose_name_plural = "Carousel Discounts"

    def __str__(self):
        return f"ID: {self.id } | URL: {self.url}"
