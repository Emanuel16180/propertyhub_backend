#!/usr/bin/env python
"""
Verificar usuarios admin existentes en cada tenant
"""

from django_tenants.utils import schema_context
from apps.tenants.models import Clinic
from apps.users.models import CustomUser

print('=== USUARIOS ADMIN EXISTENTES ===')

# Para cada clínica, mostrar usuarios admin
for clinic in Clinic.objects.all():
    print(f'\n--- {clinic.name} ({clinic.schema_name}) ---')
    with schema_context(clinic.schema_name):
        admins = CustomUser.objects.filter(is_superuser=True)
        for admin in admins:
            print(f'Email: {admin.email} | Username: {admin.username} | Activo: {admin.is_active}')
        
        if not admins:
            print('No hay usuarios admin en este tenant')

print('\n=== FIN LISTADO ===')