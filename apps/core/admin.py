"""Django admin registrations."""
from django.contrib import admin

from .models import Category, PortfolioProject, Review, ServiceType


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)


@admin.register(PortfolioProject)
class PortfolioProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "date")
    list_filter = ("category", "service_types")
    search_fields = ("name", "description", "category__name")
    autocomplete_fields = ("category",)
    filter_horizontal = ("service_types",)
    date_hierarchy = "date"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "project", "created_at")
    search_fields = ("name", "comment", "project__name")
    list_filter = ("project",)
