# config/urls_public.py
# Rutas para el tenant público (admin de tenants)

from django.urls import path, include  
from config.admin_site import public_admin_site
from tenant_debug import tenant_debug

urlpatterns = [
    path('admin/', public_admin_site.urls),
    path('debug/', tenant_debug, name='tenant_debug_public'),
    # La ruta de la API de autenticación ha sido removida
    # Solo disponible en tenants de clínicas (subdominios)
]