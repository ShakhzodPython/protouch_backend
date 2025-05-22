from django.utils import translation
from django_filters import rest_framework as filters

from .models import Product, Category


class ProductFilter(filters.FilterSet):
    title = filters.CharFilter(
        field_name="title", required=False, lookup_expr="icontains"
    )
    slug = filters.CharFilter(method="filter_by_slug")
    brand = filters.CharFilter(method="filter_by_brand")

    class Meta:
        model = Product
        fields = []

    def filter_by_slug(self, queryset, name, value):
        slugs = [slug.strip() for slug in value.split(",") if slug.strip()]
        lang = self.request.query_params.get("lang", None)
        if lang in ["ru", "uz", "en"]:
            translation.activate(lang)

        category_ids = set()

        for slug in slugs:
            if "/" in slug:
                # It's a full path to a child: find exact match
                category = Category.objects.filter(slug=slug).first()
                if category:
                    category_ids.add(category.id)
            else:
                # It's a parent: include parent and its children
                parent = Category.objects.filter(slug=slug, parent=None).first()
                if parent:
                    children_ids = parent.children.values_list("id", flat=True)
                    category_ids.add(parent.id)
                    category_ids.update(children_ids)

        if category_ids:
            return queryset.filter(categories__in=category_ids).distinct()
        return queryset.none()

    def filter_by_brand(self, queryset, name, value):
        brand_titles = [v.strip() for v in value.split(",") if v.strip()]
        return queryset.filter(brand_id__title__in=brand_titles).distinct()
