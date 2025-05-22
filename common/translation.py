from modeltranslation.translator import register, TranslationOptions

from .models import Carousel


@register(Carousel)
class CarouselTranslationOption(TranslationOptions):
    fields = ("text",)
