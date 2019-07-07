from .base import *
from .base import env

DEBUG = False
SECRET_KEY = env('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "springcm.khanna.cc"]
STATIC_ROOT = str(ROOT_DIR.path("static"))
UPLOAD_DIR = str(ROOT_DIR.path("uploads"))