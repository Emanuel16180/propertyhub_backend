#!/usr/bin/env python
"""
Crear usuarios admin para cada tenant
"""

from django_tenants.utils import schema_context
from apps.tenants.models import Clinic
from apps.users.models import CustomUser

print('=== CREANDO USUARIOS ADMIN PARA TENANTS ===')

# Para Bienestar
bienestar = Clinic.objects.get(schema_name='bienestar')
with schema_context(bienestar.schema_name):
    try:
        admin_bienestar = CustomUser.objects.create_superuser(
            email='admin@bienestar.com',
            password='admin123',
            first_name='Admin',
            last_name='Bienestar',
            user_type='admin'
        )
        print(f'✅ Admin creado para BIENESTAR: {admin_bienestar.email}')
    except Exception as e:
        print(f'⚠️ Error o ya existe: {e}')

# Para MindCare
mindcare = Clinic.objects.get(schema_name='mindcare')
with schema_context(mindcare.schema_name):
    try:
        admin_mindcare = CustomUser.objects.create_superuser(
            email='admin@mindcare.com',
            password='admin123',
            first_name='Admin',
            last_name='MindCare',
            user_type='admin'
        )
        print(f'✅ Admin creado para MINDCARE: {admin_mindcare.email}')
    except Exception as e:
        print(f'⚠️ Error o ya existe: {e}')

print('\n=== CREDENCIALES DE ACCESO ===')
print('Bienestar Admin: admin@bienestar.com / admin123')
print('MindCare Admin: admin@mindcare.com / admin123')
print('=====================================')