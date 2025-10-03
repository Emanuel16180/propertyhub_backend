# test_view.py - Vista de prueba temporal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test_tenant(request):
    from django.db import connection
    
    return JsonResponse({
        'message': 'Tenant ESPECÍFICO funcionando',
        'schema': connection.schema_name,
        'method': request.method,
        'path': request.path,
        'tenant_type': 'TENANT' if connection.schema_name != 'public' else 'PUBLIC'
    })