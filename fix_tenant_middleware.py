# fix_tenant_middleware.py
from django.db import connection
from django.conf import settings
from django.urls import clear_url_caches

class FixTenantURLConfMiddleware:
    """
    Middleware que fuerza el URLconf correcto basado en el tenant detectado
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Después de que TenantMainMiddleware procese el tenant
        if hasattr(connection, 'tenant') and connection.tenant:
            if connection.tenant.schema_name == 'public':
                # Esquema público: usar config.urls_public
                request.urlconf = 'config.urls_public'
            else:
                # Esquema de clínica: usar config.urls (con APIs)
                request.urlconf = 'config.urls'
            
            # Limpiar caché de URLs
            clear_url_caches()
        
        response = self.get_response(request)
        return response