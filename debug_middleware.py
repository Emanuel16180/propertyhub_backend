# debug_middleware.py
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

class DebugTenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log información de debug antes de la respuesta
        print(f"=== DEBUG TENANT MIDDLEWARE ===")
        print(f"Host: {request.get_host()}")
        print(f"Path: {request.path}")
        
        # Verificar información del tenant
        if hasattr(request, 'tenant'):
            print(f"Tenant: {request.tenant.schema_name} - {request.tenant.name}")
        else:
            print("No tenant found in request")
            
        # Verificar URLconf
        from django.conf import settings
        print(f"ROOT_URLCONF: {settings.ROOT_URLCONF}")
        
        if hasattr(request, 'urlconf'):
            print(f"Request URLconf: {request.urlconf}")
        else:
            print("No URLconf set on request")
            
        print(f"==============================")
        
        response = self.get_response(request)
        return response