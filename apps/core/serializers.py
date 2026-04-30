"""DRF serializers for the Senior agency backend.

Each translatable model exposes:

- The raw per-language columns (`name_uz`, `name_ru`, `name_en`, ...) — used
  for reads (so a UI can preview/edit any locale) and for writes.
- A flat resolved alias (`name`, `description`, `tasks`, ...) — read-only,
  resolved per request via `?lang=`. This makes the public read API feel
  like a normal single-language API while still letting clients send/edit
  every translation.
"""
from rest_framework import serializers

from .i18n import TranslatedField
from .models import Category, PortfolioProject, Review, ServiceType


# --------------------------------------------------------------------------- #
# Statistics                                                                  #
# --------------------------------------------------------------------------- #
class StatisticsSerializer(serializers.Serializer):
    """Read-only response shape for the live `/statistics/` endpoint."""

    total_products = serializers.IntegerField(read_only=True)
    total_service_types = serializers.IntegerField(read_only=True)


# --------------------------------------------------------------------------- #
# Category                                                                    #
# --------------------------------------------------------------------------- #
class CategorySerializer(serializers.ModelSerializer):
    name = TranslatedField("name")
    project_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "name_uz",
            "name_ru",
            "name_en",
            "project_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "name", "project_count", "created_at", "updated_at")


# --------------------------------------------------------------------------- #
# Service type                                                                #
# --------------------------------------------------------------------------- #
class ServiceTypeSerializer(serializers.ModelSerializer):
    name = TranslatedField("name")
    description = TranslatedField("description")
    what_we_do = TranslatedField("what_we_do")

    what_we_do_uz = serializers.ListField(
        child=serializers.CharField(allow_blank=False, max_length=255),
        allow_empty=True,
        required=False,
    )
    what_we_do_ru = serializers.ListField(
        child=serializers.CharField(allow_blank=False, max_length=255),
        allow_empty=True,
        required=False,
    )
    what_we_do_en = serializers.ListField(
        child=serializers.CharField(allow_blank=False, max_length=255),
        allow_empty=True,
        required=False,
    )

    class Meta:
        model = ServiceType
        fields = (
            "id",
            # resolved aliases (read-only)
            "name",
            "description",
            "what_we_do",
            # per-language columns (read+write)
            "name_uz", "name_ru", "name_en",
            "description_uz", "description_ru", "description_en",
            "what_we_do_uz", "what_we_do_ru", "what_we_do_en",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id", "name", "description", "what_we_do", "created_at", "updated_at",
        )


# --------------------------------------------------------------------------- #
# Review                                                                      #
# --------------------------------------------------------------------------- #
class ReviewSerializer(serializers.ModelSerializer):
    """Used for the standalone /reviews/ CRUD endpoints."""

    name = TranslatedField("name")
    comment = TranslatedField("comment")

    project = serializers.PrimaryKeyRelatedField(queryset=PortfolioProject.objects.all())
    project_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = (
            "id",
            "name",
            "comment",
            "name_uz", "name_ru", "name_en",
            "comment_uz", "comment_ru", "comment_en",
            "image",
            "project",
            "project_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id", "name", "comment", "project_name", "created_at", "updated_at",
        )

    def get_project_name(self, obj):
        from .i18n import get_request_language, get_translated_field
        return get_translated_field(
            obj.project, "name", get_request_language(self.context.get("request"))
        )


class ReviewNestedSerializer(serializers.ModelSerializer):
    """Read-only nested representation embedded inside a project payload."""

    name = TranslatedField("name")
    comment = TranslatedField("comment")

    class Meta:
        model = Review
        fields = ("id", "name", "comment", "image", "created_at")
        read_only_fields = fields


# --------------------------------------------------------------------------- #
# Portfolio project                                                           #
# --------------------------------------------------------------------------- #
class PortfolioProjectListSerializer(serializers.ModelSerializer):
    """Lightweight representation used in list endpoints."""

    name = TranslatedField("name")
    description = TranslatedField("description")

    category = CategorySerializer(read_only=True)
    service_types = ServiceTypeSerializer(many=True, read_only=True)

    class Meta:
        model = PortfolioProject
        fields = (
            "id",
            "name",
            "description",
            "image",
            "website_url",
            "category",
            "date",
            "service_types",
        )


class PortfolioProjectSerializer(serializers.ModelSerializer):
    """Full representation used for retrieve/create/update.

    Write side:
      - `category` accepts a Category id (dropdown in Swagger).
      - `service_types` accepts a list of ServiceType ids (multi-select).
      - `name_uz` / `description_uz` / `tasks_uz` are required; `_ru`/`_en`
        are optional and fall back to Uzbek on read.

    Read side:
      - `name`, `description`, `tasks` are resolved for the requested `?lang=`.
      - `category_detail`, `service_types_detail`, and `reviews` expose nested
        objects.
    """

    name = TranslatedField("name")
    description = TranslatedField("description")
    tasks = TranslatedField("tasks")

    tasks_uz = serializers.ListField(
        child=serializers.CharField(allow_blank=False, max_length=500),
        allow_empty=True,
        required=False,
    )
    tasks_ru = serializers.ListField(
        child=serializers.CharField(allow_blank=False, max_length=500),
        allow_empty=True,
        required=False,
    )
    tasks_en = serializers.ListField(
        child=serializers.CharField(allow_blank=False, max_length=500),
        allow_empty=True,
        required=False,
    )

    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_detail = CategorySerializer(source="category", read_only=True)

    service_types = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ServiceType.objects.all(),
    )
    service_types_detail = ServiceTypeSerializer(
        source="service_types",
        many=True,
        read_only=True,
    )
    reviews = ReviewNestedSerializer(many=True, read_only=True)

    class Meta:
        model = PortfolioProject
        fields = (
            "id",
            # resolved aliases (read-only)
            "name",
            "description",
            "tasks",
            # per-language columns (read+write)
            "name_uz", "name_ru", "name_en",
            "description_uz", "description_ru", "description_en",
            "tasks_uz", "tasks_ru", "tasks_en",
            # other
            "image",
            "website_url",
            "category",
            "category_detail",
            "service_types",
            "service_types_detail",
            "date",
            "reviews",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "name",
            "description",
            "tasks",
            "category_detail",
            "service_types_detail",
            "reviews",
            "created_at",
            "updated_at",
        )

    def validate_service_types(self, value):
        if not value:
            raise serializers.ValidationError("At least one service type is required.")
        return value
