# apps/tenants/middleware.py

from django.contrib import admin
from django.db import connection

class TenantAdminTitleMiddleware:
    """
    Middleware que modifica los títulos del admin según el tenant actual
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Modificar títulos según el tenant antes de procesar la request
        if hasattr(connection, 'tenant') and connection.tenant:
            if connection.tenant.schema_name == 'public':
                # Títulos para el admin público
                admin.site.site_header = "Administración Global de Psico SAS"
                admin.site.site_title = "Admin Global"
                admin.site.index_title = "Gestión de Clínicas"
            else:
                # Títulos para admins de tenants
                tenant_name = getattr(connection.tenant, 'name', 'Clínica')
                admin.site.site_header = f"Administración de {tenant_name}"
                admin.site.site_title = "Admin Clínica"
                admin.site.index_title = "Panel de Control"
        
        response = self.get_response(request)
        return response