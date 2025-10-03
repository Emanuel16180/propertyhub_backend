#!/usr/bin/env python
"""
Diagnóstico completo de resolución de URLs en django-tenants
"""

import django_tenants
from django_tenants.utils import get_tenant_model
from apps.tenants.models import Clinic, Domain
from django.conf import settings
from django.db import connection
from django.urls import get_resolver
from django.core.urlresolvers import reverse

print('=== DIAGNÓSTICO COMPLETO DE URLs ===')
print(f'Django-tenants version: {django_tenants.VERSION}')

print('\n=== CONFIGURACIÓN DE URLs ===')
print(f'ROOT_URLCONF: {settings.ROOT_URLCONF}')
print(f'TENANT_URLCONF: {settings.TENANT_URLCONF}')

print('\n=== SCHEMA ACTUAL ===')
print(f'Schema actual: {connection.schema_name if hasattr(connection, "schema_name") else "No definido"}')

print('\n=== RESOLVER ACTUAL ===')
resolver = get_resolver()
print(f'URL resolver: {resolver}')
print(f'URL patterns: {len(resolver.url_patterns)} patterns')

print('\n=== PATTERNS PRINCIPALES ===')
for i, pattern in enumerate(resolver.url_patterns[:10]):  # Solo primeros 10
    print(f'{i}: {pattern.pattern} -> {pattern.callback if hasattr(pattern, "callback") else "No callback"}')

print('\n=== MIDDLEWARE EN CONFIGURACIÓN ===')
for i, middleware in enumerate(settings.MIDDLEWARE):
    status = "✅" if "TenantMainMiddleware" in middleware else "  "
    print(f'{status} {i}: {middleware}')

print('\n=== TENANT INFO ===')
if hasattr(connection, 'tenant'):
    print(f'Tenant actual: {connection.tenant}')
    print(f'Schema name: {connection.tenant.schema_name}')
else:
    print('No hay información de tenant en connection')

print('\n=== DOMINIOS REGISTRADOS ===')
for domain in Domain.objects.all():
    print(f'  {domain.domain} -> {domain.tenant.schema_name} (primary: {domain.is_primary})')

print('\n=== FIN DIAGNÓSTICO ===')