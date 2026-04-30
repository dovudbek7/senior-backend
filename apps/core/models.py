"""Database models for the Senior agency backend.

Multilingual fields are stored at the column level: every translatable
attribute exists three times — `<name>_uz`, `<name>_ru`, `<name>_en`.

Uzbek (`_uz`) is the primary language and is always required.
Russian and English are optional; the API falls back to Uzbek when a
translation is missing.
"""
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base providing created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    """A portfolio project category (e.g. Landing, E-commerce, Dashboard)."""

    name_uz = models.CharField(max_length=100, unique=True)
    name_ru = models.CharField(max_length=100, blank=True, default="")
    name_en = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        ordering = ("name_uz",)
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name_uz


class ServiceType(TimeStampedModel):
    """A service the agency provides (e.g. SMM, Web Development)."""

    name_uz = models.CharField(max_length=150, unique=True)
    name_ru = models.CharField(max_length=150, blank=True, default="")
    name_en = models.CharField(max_length=150, blank=True, default="")

    description_uz = models.TextField()
    description_ru = models.TextField(blank=True, default="")
    description_en = models.TextField(blank=True, default="")

    what_we_do_uz = models.JSONField(default=list, blank=True)
    what_we_do_ru = models.JSONField(default=list, blank=True)
    what_we_do_en = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ("name_uz",)

    def __str__(self) -> str:
        return self.name_uz


class PortfolioProject(TimeStampedModel):
    """A delivered project shown on the agency portfolio."""

    name_uz = models.CharField(max_length=200)
    name_ru = models.CharField(max_length=200, blank=True, default="")
    name_en = models.CharField(max_length=200, blank=True, default="")

    description_uz = models.TextField()
    description_ru = models.TextField(blank=True, default="")
    description_en = models.TextField(blank=True, default="")

    tasks_uz = models.JSONField(default=list, blank=True)
    tasks_ru = models.JSONField(default=list, blank=True)
    tasks_en = models.JSONField(default=list, blank=True)

    image = models.ImageField(upload_to="portfolio/")
    website_url = models.URLField(blank=True)
    date = models.DateField()

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="projects",
    )
    service_types = models.ManyToManyField(
        ServiceType,
        related_name="projects",
        blank=False,
    )

    class Meta:
        ordering = ("-date", "-created_at")

    def __str__(self) -> str:
        return self.name_uz


class Review(TimeStampedModel):
    """A client review attached to a specific portfolio project."""

    name_uz = models.CharField(max_length=150)
    name_ru = models.CharField(max_length=150, blank=True, default="")
    name_en = models.CharField(max_length=150, blank=True, default="")

    comment_uz = models.TextField()
    comment_ru = models.TextField(blank=True, default="")
    comment_en = models.TextField(blank=True, default="")

    image = models.ImageField(upload_to="reviews/", blank=True, null=True)

    project = models.ForeignKey(
        PortfolioProject,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.name_uz} → {self.project.name_uz}"
