"""FilterSets for the core app.

Filtering operates on the canonical (Uzbek) name columns when matching
by name, since that is the primary language of the agency.
"""
import django_filters

from .models import PortfolioProject, Review


class PortfolioProjectFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name="category__id")
    category_name = django_filters.CharFilter(
        field_name="category__name_uz",
        lookup_expr="iexact",
    )
    service_type = django_filters.NumberFilter(field_name="service_types__id")
    service_type_name = django_filters.CharFilter(
        field_name="service_types__name_uz",
        lookup_expr="iexact",
    )
    date_from = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = PortfolioProject
        fields = (
            "category",
            "category_name",
            "service_type",
            "service_type_name",
            "date_from",
            "date_to",
        )


class ReviewFilter(django_filters.FilterSet):
    project = django_filters.NumberFilter(field_name="project__id")

    class Meta:
        model = Review
        fields = ("project",)
