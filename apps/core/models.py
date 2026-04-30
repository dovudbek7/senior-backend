"""Database models for the Senior agency backend."""
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base providing created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    """A portfolio project category (e.g. Landing, E-commerce, Dashboard)."""

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name


class ServiceType(TimeStampedModel):
    """A service the agency provides (e.g. SMM, Web Development)."""

    name = models.CharField(max_length=150, unique=True)
    description = models.TextField()
    what_we_do = models.JSONField(
        default=list,
        blank=True,
        help_text="List of strings describing concrete deliverables under this service type.",
    )

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class PortfolioProject(TimeStampedModel):
    """A delivered project shown on the agency portfolio."""

    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to="portfolio/")
    website_url = models.URLField(blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="projects",
    )
    date = models.DateField()
    tasks = models.JSONField(
        default=list,
        blank=True,
        help_text="List of strings describing the tasks completed in this project.",
    )
    description = models.TextField()

    service_types = models.ManyToManyField(
        ServiceType,
        related_name="projects",
        blank=False,
    )

    class Meta:
        ordering = ("-date", "-created_at")

    def __str__(self) -> str:
        return self.name


class Review(TimeStampedModel):
    """A client review attached to a specific portfolio project."""

    name = models.CharField(max_length=150)
    comment = models.TextField()
    image = models.ImageField(upload_to="reviews/", blank=True, null=True)

    project = models.ForeignKey(
        PortfolioProject,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.name} → {self.project.name}"
