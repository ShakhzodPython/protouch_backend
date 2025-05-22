from modeltranslation.translator import register, TranslationOptions

from .models import Category, Product, ProductDetail


@register(Category)
class CategoryTranslationOption(TranslationOptions):
    fields = ("title",)


@register(ProductDetail)
class ProductDetailTranslationOption(TranslationOptions):
    fields = ("key", "value")


@register(Product)
class ProductTranslationOption(TranslationOptions):
    fields = ("title", "short_description", "description")
