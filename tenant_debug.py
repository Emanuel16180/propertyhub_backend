# tenant_debug.py - Vista de diagnóstico para verificar tenant actual
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

@csrf_exempt
def tenant_debug(request):
    """Vista para diagnosticar qué tenant se está usando"""
    from django_tenants.utils import get_tenant_model
    
    try:
        # Información del tenant actual
        tenant_info = {
            'schema_name': connection.schema_name,
            'domain_requested': request.get_host(),
            'path': request.path,
            'method': request.method,
        }
        
        # Verificar si tenemos acceso a tenant
        if hasattr(connection, 'tenant'):
            tenant_info['tenant_name'] = getattr(connection.tenant, 'name', 'N/A')
            tenant_info['tenant_id'] = getattr(connection.tenant, 'id', 'N/A')
        else:
            tenant_info['tenant_name'] = 'NO TENANT OBJECT'
            
        # Verificar qué URLs están disponibles
        from django.urls import get_resolver
        resolver = get_resolver()
        
        available_urls = []
        for pattern in resolver.url_patterns[:5]:  # Solo los primeros 5
            available_urls.append(str(pattern.pattern))
            
        tenant_info['available_urls'] = available_urls
        
        # Verificar si estamos en public o tenant schema
        if connection.schema_name == 'public':
            tenant_info['tenant_type'] = 'PUBLIC SCHEMA'
        else:
            tenant_info['tenant_type'] = 'TENANT SCHEMA'
            
        return JsonResponse({
            'status': 'success',
            'tenant_info': tenant_info
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'schema_name': connection.schema_name,
            'domain': request.get_host()
        })