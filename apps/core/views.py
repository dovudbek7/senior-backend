"""ViewSets exposing the Senior agency CRUD endpoints.

Every list/retrieve endpoint accepts a `?lang=` query parameter
(`uz` | `ru` | `en`). Search runs against the Uzbek (default) columns.
"""
from django.db.models import Count
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import PortfolioProjectFilter, ReviewFilter
from .i18n import LANGUAGES, DEFAULT_LANGUAGE
from .models import Category, PortfolioProject, Review, ServiceType
from .serializers import (
    CategorySerializer,
    PortfolioProjectListSerializer,
    PortfolioProjectSerializer,
    ReviewSerializer,
    ServiceTypeSerializer,
    StatisticsSerializer,
)


# Reusable Swagger query parameter for language switching.
LANG_PARAM = openapi.Parameter(
    "lang",
    openapi.IN_QUERY,
    description=(
        "Language for resolved fields (`name`, `description`, `tasks`, "
        "`comment`, `what_we_do`). Defaults to Uzbek."
    ),
    type=openapi.TYPE_STRING,
    enum=list(LANGUAGES),
    default=DEFAULT_LANGUAGE,
    required=False,
)


def with_lang_param(viewset_cls):
    """Class decorator that adds the `lang` query parameter to the
    Swagger schema of `list` and `retrieve` actions.
    """
    decorator = swagger_auto_schema(manual_parameters=[LANG_PARAM])
    for method_name in ("list", "retrieve"):
        viewset_cls = method_decorator(
            name=method_name, decorator=decorator
        )(viewset_cls)
    return viewset_cls


class StatisticsView(APIView):
    """Read-only endpoint that returns live, auto-calculated counters.

    Values are computed on every request — nothing is persisted.
    """

    @swagger_auto_schema(
        operation_summary="Get live agency statistics",
        operation_description=(
            "Returns real-time counts computed directly from the database:\n"
            "- `total_products` — number of PortfolioProject rows\n"
            "- `total_service_types` — number of ServiceType rows"
        ),
        responses={200: StatisticsSerializer()},
        tags=["statistics"],
    )
    def get(self, request, *args, **kwargs):
        data = {
            "total_products": PortfolioProject.objects.count(),
            "total_service_types": ServiceType.objects.count(),
        }
        return Response(StatisticsSerializer(data).data)


@with_lang_param
class CategoryViewSet(viewsets.ModelViewSet):
    """Full CRUD for Category."""

    queryset = Category.objects.all().annotate(project_count=Count("projects"))
    serializer_class = CategorySerializer
    search_fields = ("name_uz",)
    ordering_fields = ("name_uz", "created_at")


@with_lang_param
class ServiceTypeViewSet(viewsets.ModelViewSet):
    """Full CRUD for ServiceType."""

    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    search_fields = ("name_uz", "description_uz")
    ordering_fields = ("name_uz", "created_at", "updated_at")


class PortfolioProjectViewSet(viewsets.ModelViewSet):
    """Full CRUD for PortfolioProject with filtering, search, and pagination."""

    queryset = (
        PortfolioProject.objects.all()
        .select_related("category")
        .prefetch_related("service_types", "reviews")
    )
    filterset_class = PortfolioProjectFilter
    # Search runs against Uzbek (primary) columns only.
    search_fields = ("name_uz", "description_uz", "category__name_uz")
    ordering_fields = ("date", "name_uz", "created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return PortfolioProjectListSerializer
        return PortfolioProjectSerializer

    @swagger_auto_schema(
        manual_parameters=[
            LANG_PARAM,
            openapi.Parameter(
                "category",
                openapi.IN_QUERY,
                description="Filter by Category id.",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "category_name",
                openapi.IN_QUERY,
                description="Filter by Category Uzbek name (case-insensitive exact).",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "service_type",
                openapi.IN_QUERY,
                description="Filter by ServiceType id.",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "service_type_name",
                openapi.IN_QUERY,
                description="Filter by ServiceType Uzbek name (case-insensitive exact).",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search Uzbek (primary) columns: project name, description, category.",
                type=openapi.TYPE_STRING,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[LANG_PARAM])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="List reviews for a single project",
        manual_parameters=[LANG_PARAM],
        responses={200: ReviewSerializer(many=True)},
    )
    @action(detail=True, methods=["get"], url_path="reviews")
    def reviews(self, request, pk=None):
        project = self.get_object()
        page = self.paginate_queryset(project.reviews.all())
        serializer = ReviewSerializer(
            page if page is not None else project.reviews.all(),
            many=True,
            context={"request": request},
        )
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


@with_lang_param
class ReviewViewSet(viewsets.ModelViewSet):
    """Full CRUD for Review. Each review must belong to a PortfolioProject."""

    queryset = Review.objects.select_related("project").all()
    serializer_class = ReviewSerializer
    filterset_class = ReviewFilter
    search_fields = ("name_uz", "comment_uz", "project__name_uz")
    ordering_fields = ("created_at", "name_uz")
