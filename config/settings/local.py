from .base import *
from .base import env

DEBUG = True
SECRET_KEY = env('DJANGO_SECRET_KEY', default="!LOCAL SECRET KEY!")
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

INSTALLED_APPS = ['debug_toolbar'] + INSTALLED_APPS
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
INTERNAL_IPS = ['127.0.0.1']
UPLOAD_DIR = str(ROOT_DIR.path("uploads"))