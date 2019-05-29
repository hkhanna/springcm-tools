from .base import *
from .base import env

DEBUG = True
SECRET_KEY = env('DJANGO_SECRET_KEY', default="!LOCAL SECRET KEY!")
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]