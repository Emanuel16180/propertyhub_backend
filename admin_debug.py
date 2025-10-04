from django.http import JsonResponse
from django.urls import get_resolver
from django.conf import settings
from django.db import connection

def admin_debug(request):
    """Vista para debug específico del admin"""
    resolver = get_resolver()
    
    # Buscar qué admin site se está usando
    admin_pattern = None
    for pattern in resolver.url_patterns:
        if str(pattern.pattern) == 'admin/':
            admin_pattern = pattern
            break
    
    info = {
        'schema': connection.schema_name,
        'urlconf': resolver.urlconf_name,
        'root_urlconf': settings.ROOT_URLCONF,
        'tenant_urlconf': settings.TENANT_URLCONF,
        'admin_pattern': str(admin_pattern) if admin_pattern else 'No encontrado',
        'total_patterns': len(resolver.url_patterns),
        'patterns': [str(p.pattern) for p in resolver.url_patterns[:10]]
    }
    
    return JsonResponse(info)