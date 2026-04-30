"""WSGI config for the senior project."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "senior.settings")

application = get_wsgi_application()
