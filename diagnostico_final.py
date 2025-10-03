#!/usr/bin/env python
"""
Script de diagnóstico completo para django-tenants
Ejecutar con: python manage.py shell < diagnostico_final.py
"""

import django_tenants
from django_tenants.utils import get_tenant_model
from apps.tenants.models import Clinic, Domain
from django.conf import settings
from django.db import connection

print('=== DIAGNÓSTICO DJANGO-TENANTS ===')
print(f'Django-tenants version: {django_tenants.VERSION}')
print(f'Tenant model: {get_tenant_model()}')

print('\n=== TENANTS EXISTENTES ===')
for clinic in Clinic.objects.all():
    print(f'Clínica: {clinic.name} | Schema: {clinic.schema_name}')

print('\n=== DOMINIOS EXISTENTES ===')
for domain in Domain.objects.all():
    print(f'Dominio: {domain.domain} -> Schema: {domain.tenant.schema_name} | Primary: {domain.is_primary}')

print('\n=== CONFIGURACIONES CRÍTICAS ===')
print(f'ROOT_URLCONF: {settings.ROOT_URLCONF}')
print(f'TENANT_URLCONF: {settings.TENANT_URLCONF}')
print(f'DATABASE_BACKEND: {settings.DATABASES["default"]["ENGINE"]}')

print('\n=== MIDDLEWARE ORDEN ===')
for i, middleware in enumerate(settings.MIDDLEWARE):
    print(f'{i}: {middleware}')

print('\n=== SCHEMA ACTUAL ===')
print(f'Schema actual: {connection.schema_name if hasattr(connection, "schema_name") else "No definido"}')

print('\n=== SHARED_APPS vs TENANT_APPS ===')
print(f'SHARED_APPS: {len(settings.SHARED_APPS)} apps')
for app in settings.SHARED_APPS:
    print(f'  - {app}')

print(f'\nTENANT_APPS: {len(settings.TENANT_APPS)} apps')
for app in settings.TENANT_APPS:
    print(f'  - {app}')

print('\n=== FIN DIAGNÓSTICO ===')