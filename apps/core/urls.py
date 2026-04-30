"""URL routing for the core app."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    PortfolioProjectViewSet,
    ReviewViewSet,
    ServiceTypeViewSet,
    StatisticsView,
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"service-types", ServiceTypeViewSet, basename="service-type")
router.register(r"projects", PortfolioProjectViewSet, basename="project")
router.register(r"reviews", ReviewViewSet, basename="review")

urlpatterns = [
    path("statistics/", StatisticsView.as_view(), name="statistics"),
    path("", include(router.urls)),
]
