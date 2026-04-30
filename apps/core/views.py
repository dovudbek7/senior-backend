"""ViewSets exposing the Senior agency CRUD endpoints."""
from django.db.models import Count
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import PortfolioProjectFilter, ReviewFilter
from .models import Category, PortfolioProject, Review, ServiceType
from .serializers import (
    CategorySerializer,
    PortfolioProjectListSerializer,
    PortfolioProjectSerializer,
    ReviewSerializer,
    ServiceTypeSerializer,
    StatisticsSerializer,
)


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


class CategoryViewSet(viewsets.ModelViewSet):
    """Full CRUD for Category."""

    queryset = Category.objects.all().annotate(project_count=Count("projects"))
    serializer_class = CategorySerializer
    search_fields = ("name",)
    ordering_fields = ("name", "created_at")


class ServiceTypeViewSet(viewsets.ModelViewSet):
    """Full CRUD for ServiceType."""

    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    search_fields = ("name", "description")
    ordering_fields = ("name", "created_at", "updated_at")


class PortfolioProjectViewSet(viewsets.ModelViewSet):
    """Full CRUD for PortfolioProject with filtering, search, and pagination."""

    queryset = (
        PortfolioProject.objects.all()
        .select_related("category")
        .prefetch_related("service_types", "reviews")
    )
    filterset_class = PortfolioProjectFilter
    search_fields = ("name", "description", "category__name")
    ordering_fields = ("date", "name", "created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return PortfolioProjectListSerializer
        return PortfolioProjectSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "category",
                openapi.IN_QUERY,
                description="Filter by Category id.",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "category_name",
                openapi.IN_QUERY,
                description="Filter by Category name (case-insensitive exact).",
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
                description="Filter by ServiceType name (case-insensitive exact).",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search in project name, description, and category name.",
                type=openapi.TYPE_STRING,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="List reviews for a single project",
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


class ReviewViewSet(viewsets.ModelViewSet):
    """Full CRUD for Review. Each review must belong to a PortfolioProject."""

    queryset = Review.objects.select_related("project").all()
    serializer_class = ReviewSerializer
    filterset_class = ReviewFilter
    search_fields = ("name", "comment", "project__name")
    ordering_fields = ("created_at", "name")
