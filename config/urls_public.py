# config/urls_public.py
# Rutas para el tenant público (gestión de clínicas)

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]