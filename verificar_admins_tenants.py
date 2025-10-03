#!/usr/bin/env python
"""
Verificar usuarios admin existentes en tenants (no public)
"""

from django_tenants.utils import schema_context
from apps.tenants.models import Clinic
from apps.users.models import CustomUser

print('=== USUARIOS ADMIN EN TENANTS ===')

# Para cada clínica que NO sea public
for clinic in Clinic.objects.exclude(schema_name='public'):
    print(f'\n--- {clinic.name} ({clinic.schema_name}) ---')
    with schema_context(clinic.schema_name):
        admins = CustomUser.objects.filter(is_superuser=True)
        for admin in admins:
            print(f'Email: {admin.email} | Username: {admin.username} | Activo: {admin.is_active}')
        
        if not admins:
            print('No hay usuarios admin en este tenant')

print('\n=== FIN LISTADO ===')