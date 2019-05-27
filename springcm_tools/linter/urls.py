from django.urls import path
from . import views

app_name = 'linter'
urlpatterns = [
    path('', views.index, name='index'),
]