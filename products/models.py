import os
import uuid
from decimal import Decimal

from PIL import Image
from io import BytesIO

from django.db import models
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.utils import timezone
from django.core.exceptions import ValidationError
from mptt.models import MPTTModel, TreeForeignKey

from core import settings
from common.models import File
from utils.base import BaseModel


# Create your models here.


class Brand(BaseModel):
    title = models.CharField(max_length=225, verbose_name="Title")

    def __str__(self):
        return self.title


class Category(MPTTModel):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, unique=True, editable=False
    )
    title = models.CharField(max_length=255, verbose_name="Title")
    slug = models.SlugField(unique=True, blank=True, null=True)
    brands = models.ManyToManyField(Brand, blank=True, related_name="categories")
    is_carousel = models.BooleanField(default=False, verbose_name="Carousel")
    image_id = models.ForeignKey(
        File, verbose_name="Image", null=True, blank=True, on_delete=models.CASCADE
    )
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    def generate_slug(self):
        base_slug = slugify(self.title_en)
        if self.parent:
            return f"{self.parent.slug}/{base_slug}"
        return base_slug

    def save(self, *args, **kwargs):
        if not self.slug or self.slug != self.generate_slug():
            self.slug = self.generate_slug()

        original_slug = self.slug
        counter = 1
        while Category.objects.filter(slug=self.slug).exclude(id=self.id).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    class MPTTMeta:
        order_insertion_by = ["title"]

    def __str__(self):
        return str(self.title)


class Product(BaseModel):
    title = models.CharField(max_length=255, verbose_name="Title")
    slug = models.SlugField(unique=True, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    short_description = models.CharField(
        max_length=255, verbose_name="Short description"
    )
    description = models.TextField(verbose_name="Description")
    is_in_stock = models.BooleanField(default=True, verbose_name="In stock")
    is_pre_order = models.BooleanField(default=False, verbose_name="Pre order")
    brand_id = models.ForeignKey(Brand, verbose_name="Brand", on_delete=models.PROTECT)
    categories = models.ManyToManyField(Category, related_name="products")

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def clean(self):
        # Ensure slug is generated before validation
        if not self.slug:
            self.slug = slugify(self.title_en)

        if Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            raise ValidationError({"slug": "This slug is already taken."})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title_en)

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.title)


class ProductDetail(BaseModel):
    product_id = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_details"
    )
    key = models.CharField(max_length=255, verbose_name="Key")
    value = models.CharField(max_length=255, verbose_name="Value")

    class Meta:
        verbose_name = "Product Detail"
        verbose_name_plural = "Product Details"

    def __str__(self):
        return (
            f"Product: {self.product_id.title} | Key: {self.key} | Value: {self.value}"
        )


class ProductDiscount(BaseModel):
    product = models.OneToOneField(
        Product,
        verbose_name="Product",
        on_delete=models.CASCADE,
        related_name="discount",
    )
    percent = models.PositiveIntegerField(verbose_name="Percent")
    start_date = models.DateTimeField(verbose_name="Start date")
    end_date = models.DateTimeField(verbose_name="End date")

    class Meta:
        verbose_name = "Product Discount"
        verbose_name_plural = "Product Discounts"

    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    def discounted_price(self):
        if self.is_active():
            discount = self.product.price * Decimal(self.percent) / Decimal(100)
            return self.product.price - discount
        return self.product.price

    def __str__(self):
        return f"{self.product.title} - {self.percent}%"


class ProductImage(BaseModel):
    product_id = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_images"
    )
    image = models.ImageField(upload_to="uploads/products/files")
    order = models.PositiveIntegerField(
        default=0, verbose_name="Order", null=False, blank=False
    )

    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        ordering = ["order"]

    def save(self, *args, **kwargs):
        is_webp = self.image.name.lower().endswith(".webp")
        original_path = None

        if not is_webp and self.image:
            original_path = os.path.join(
                settings.MEDIA_ROOT + "/uploads/products/files", self.image.name
            )
        super().save(*args, **kwargs)

        if not is_webp:
            image = Image.open(self.image)
            image = image.convert("RGBA")

            webp_io = BytesIO()
            image.save(webp_io, format("WEBP"), quality=80)

            webp_path = os.path.splitext(os.path.basename(self.image.name))[0] + ".webp"
            self.image.save(webp_path, ContentFile(webp_io.getvalue()), save=False)
            super().save(*args, **kwargs)

            # Deleting original image
            if original_path and os.path.exists(original_path):
                os.remove(original_path)

    def __str__(self):
        return f"Image for {self.product_id} | Order: {self.order}"
