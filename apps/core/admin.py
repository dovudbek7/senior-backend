"""Django admin registrations.

Translatable models present each language as its own collapsible
fieldset so editors can fill translations side by side.
"""
from django.contrib import admin

from .models import Category, PortfolioProject, Review, ServiceType


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name_uz", "created_at")
    search_fields = ("name_uz", "name_ru", "name_en")

    fieldsets = (
        ("Uzbek (default)", {"fields": ("name_uz",)}),
        ("Russian", {"fields": ("name_ru",), "classes": ("collapse",)}),
        ("English", {"fields": ("name_en",), "classes": ("collapse",)}),
    )


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name_uz", "created_at")
    search_fields = ("name_uz", "name_ru", "name_en")

    fieldsets = (
        ("Uzbek (default)", {
            "fields": ("name_uz", "description_uz", "what_we_do_uz"),
        }),
        ("Russian", {
            "fields": ("name_ru", "description_ru", "what_we_do_ru"),
            "classes": ("collapse",),
        }),
        ("English", {
            "fields": ("name_en", "description_en", "what_we_do_en"),
            "classes": ("collapse",),
        }),
    )


@admin.register(PortfolioProject)
class PortfolioProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name_uz", "category", "date")
    list_filter = ("category", "service_types")
    search_fields = ("name_uz", "description_uz", "category__name_uz")
    autocomplete_fields = ("category",)
    filter_horizontal = ("service_types",)
    date_hierarchy = "date"

    fieldsets = (
        ("Project metadata", {
            "fields": (
                "image",
                "website_url",
                "category",
                "service_types",
                "date",
            ),
        }),
        ("Uzbek (default)", {
            "fields": ("name_uz", "description_uz", "tasks_uz"),
        }),
        ("Russian", {
            "fields": ("name_ru", "description_ru", "tasks_ru"),
            "classes": ("collapse",),
        }),
        ("English", {
            "fields": ("name_en", "description_en", "tasks_en"),
            "classes": ("collapse",),
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "name_uz", "project", "created_at")
    search_fields = ("name_uz", "comment_uz", "project__name_uz")
    list_filter = ("project",)

    fieldsets = (
        ("Review metadata", {"fields": ("project", "image")}),
        ("Uzbek (default)", {"fields": ("name_uz", "comment_uz")}),
        ("Russian", {
            "fields": ("name_ru", "comment_ru"),
            "classes": ("collapse",),
        }),
        ("English", {
            "fields": ("name_en", "comment_en"),
            "classes": ("collapse",),
        }),
    )
