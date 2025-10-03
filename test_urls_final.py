#!/usr/bin/env python
"""
Test final de URLs por tenant
"""

from django.test import Client
from django.urls import reverse
import requests

print('=== TEST FINAL DE URLs POR TENANT ===')

# Test tenant público
print('\n--- TENANT PÚBLICO (localhost) ---')
try:
    response = requests.get('http://localhost:8000/debug/', timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f'✅ Schema: {data["tenant_info"]["schema_name"]}')
        print(f'✅ Available URLs: {len(data["tenant_info"]["available_urls"])} patterns')
    else:
        print(f'❌ Error: {response.status_code}')
except Exception as e:
    print(f'❌ Error connecting: {e}')

# Test API en tenant público (debe dar 404)
try:
    response = requests.get('http://localhost:8000/api/professionals/', timeout=5)
    if response.status_code == 404:
        print('✅ API professionals da 404 (correcto)')
    else:
        print(f'❌ API professionals responde {response.status_code} (incorrecto)')
except Exception as e:
    print(f'❌ Error: {e}')

# Test tenant Bienestar
print('\n--- TENANT BIENESTAR ---')
try:
    response = requests.get('http://bienestar.localhost:8000/debug/', timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f'✅ Schema: {data["tenant_info"]["schema_name"]}')
        print(f'✅ Available URLs: {len(data["tenant_info"]["available_urls"])} patterns')
    else:
        print(f'❌ Error: {response.status_code}')
except Exception as e:
    print(f'❌ Error connecting: {e}')

# Test API en tenant Bienestar (debe funcionar)
try:
    response = requests.get('http://bienestar.localhost:8000/api/professionals/', timeout=5)
    if response.status_code in [200, 401]:  # 200 o 401 (sin auth) es correcto
        print(f'✅ API professionals responde {response.status_code} (funciona)')
    else:
        print(f'❌ API professionals responde {response.status_code}')
except Exception as e:
    print(f'❌ Error: {e}')

print('\n=== FIN TEST ===')