"""
WSGI config for springcm_tools project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
os.environ.setdefault('DJANGO_READ_DOT_ENV_FILE', 'True')

application = get_wsgi_application()
