"""DRF serializers for the Senior agency backend."""
from rest_framework import serializers

from .models import Category, PortfolioProject, Review, ServiceType


class StatisticsSerializer(serializers.Serializer):
    """Read-only response shape for the live `/statistics/` endpoint."""

    total_products = serializers.IntegerField(read_only=True)
    total_service_types = serializers.IntegerField(read_only=True)


class CategorySerializer(serializers.ModelSerializer):
    project_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "project_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "project_count", "created_at", "updated_at")


class ServiceTypeSerializer(serializers.ModelSerializer):
    what_we_do = serializers.ListField(
        child=serializers.CharField(allow_blank=False, max_length=255),
        allow_empty=True,
        required=False,
    )

    class Meta:
        model = ServiceType
        fields = (
            "id",
            "name",
            "description",
            "what_we_do",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ReviewSerializer(serializers.ModelSerializer):
    """Used for the standalone /reviews/ CRUD endpoints."""

    project = serializers.PrimaryKeyRelatedField(queryset=PortfolioProject.objects.all())
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = Review
        fields = (
            "id",
            "name",
            "comment",
            "image",
            "project",
            "project_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "project_name", "created_at", "updated_at")


class ReviewNestedSerializer(serializers.ModelSerializer):
    """Read-only nested representation embedded inside a project payload."""

    class Meta:
        model = Review
        fields = ("id", "name", "comment", "image", "created_at")
        read_only_fields = fields


class PortfolioProjectListSerializer(serializers.ModelSerializer):
    """Lightweight representation used in list endpoints."""

    category = CategorySerializer(read_only=True)
    service_types = ServiceTypeSerializer(many=True, read_only=True)

    class Meta:
        model = PortfolioProject
        fields = (
            "id",
            "name",
            "image",
            "website_url",
            "category",
            "date",
            "description",
            "service_types",
        )


class PortfolioProjectSerializer(serializers.ModelSerializer):
    """Full representation used for retrieve/create/update.

    Write side:
      - `category` accepts a Category id (dropdown in Swagger).
      - `service_types` accepts a list of ServiceType ids (multi-select in Swagger).

    Read side:
      - `category_detail` and `service_types_detail` expose the nested objects.
    """

    tasks = serializers.ListField(
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
            "name",
            "image",
            "website_url",
            "category",
            "category_detail",
            "date",
            "tasks",
            "description",
            "service_types",
            "service_types_detail",
            "reviews",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
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
