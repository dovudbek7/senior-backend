"""ASGI config for the senior project."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "senior.settings")

application = get_asgi_application()
