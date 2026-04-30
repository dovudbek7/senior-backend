"""Database-level i18n helpers.

The project stores translations as separate columns per language:
`name_uz`, `name_ru`, `name_en`. These helpers resolve the right column
based on the current request's `lang` query parameter and provide a
reusable DRF field for read-side serialization.
"""
from rest_framework import serializers

LANGUAGES = ("uz", "ru", "en")
DEFAULT_LANGUAGE = "uz"


def get_request_language(request) -> str:
    """Return the language code requested via `?lang=` (uz/ru/en).

    Falls back to Uzbek (the agency's primary language) when the
    parameter is missing or unrecognized.
    """
    if request is None:
        return DEFAULT_LANGUAGE

    lang = None
    query_params = getattr(request, "query_params", None)
    if query_params is not None:
        lang = query_params.get("lang")
    if lang is None:
        get = getattr(request, "GET", None)
        if get is not None:
            lang = get.get("lang")

    if lang in LANGUAGES:
        return lang
    return DEFAULT_LANGUAGE


def get_translated_field(obj, base: str, lang: str):
    """Return ``obj.<base>_<lang>``, falling back to the default language.

    Empty strings and empty lists are treated as missing so that the
    Uzbek value is used instead.
    """
    value = getattr(obj, f"{base}_{lang}", None)
    if value in (None, "", []):
        return getattr(obj, f"{base}_{DEFAULT_LANGUAGE}", None)
    return value


class TranslatedField(serializers.Field):
    """Read-only serializer field that resolves a multilingual column.

    Usage::

        name = TranslatedField("name")          # reads name_uz / name_ru / name_en
        tasks = TranslatedField("tasks")        # reads tasks_uz / ...

    The active language is determined by the `request` in the
    serializer context (via `?lang=`), with Uzbek as fallback.
    """

    def __init__(self, base: str, **kwargs):
        self.base = base
        kwargs.setdefault("read_only", True)
        super().__init__(**kwargs)

    def get_attribute(self, instance):
        return instance

    def to_representation(self, instance):
        lang = get_request_language(self.context.get("request"))
        return get_translated_field(instance, self.base, lang)
