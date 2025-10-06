#!/usr/bin/env python
"""
Comando para crear administradores de clínica y repoblar datos
"""

import os
import sys
import django
from django.db import connection

# Configurar Django
sys.path.append('c:/Users/asus/Documents/psico_admin_sp1_despliegue')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django_tenants.utils import schema_context
from apps.tenants.models import Clinic
from apps.users.models import CustomUser
from apps.clinic_admin.models import ClinicAdmin

def create_clinic_admins():
    """Crear administradores para cada clínica"""
    
    print("🔧 Creación de Administradores de Clínica")
    print("=" * 50)
    
    # Obtener todas las clínicas (excluyendo public)
    clinics = Clinic.objects.exclude(schema_name='public')
    
    for clinic in clinics:
        print(f"\n🏥 Procesando clínica: {clinic.name} (schema: {clinic.schema_name})")
        
        # Cambiar al contexto del tenant
        with schema_context(clinic.schema_name):
            # Verificar si ya existe el admin
            admin_exists = CustomUser.objects.filter(
                email='admin@gmail.com'
            ).exists()
            
            if admin_exists:
                print(f"   ✅ Admin ya existe")
            else:
                # Crear el usuario administrador
                admin_user = CustomUser.objects.create_user(
                    email='admin@gmail.com',
                    password='admin',
                    first_name='Admin',
                    last_name=clinic.name,
                    user_type='admin',
                    ci='99999999'  # CI ficticio para admin
                )
                print(f"   ✅ Usuario admin creado")
                
                # Crear el perfil de admin de clínica
                clinic_admin = ClinicAdmin.objects.create(
                    user=admin_user,
                    clinic=clinic,
                    permissions=['all']  # Todos los permisos
                )
                print(f"   ✅ ClinicAdmin creado con todos los permisos")
                
                print(f"   📧 Email: admin@gmail.com")
                print(f"   🔐 Contraseña: admin")

def populate_tenant_data():
    """Poblar datos específicos por tenant"""
    
    print(f"\n🌱 Poblando datos por tenant")
    print("=" * 40)
    
    clinics = Clinic.objects.exclude(schema_name='public')
    
    for clinic in clinics:
        print(f"\n🏥 Poblando {clinic.name}...")
        
        with schema_context(clinic.schema_name):
            # Contar usuarios existentes
            patient_count = CustomUser.objects.filter(user_type='patient').count()
            professional_count = CustomUser.objects.filter(user_type='professional').count()
            
            print(f"   📊 Estado actual:")
            print(f"   - Pacientes: {patient_count}")
            print(f"   - Profesionales: {professional_count}")
            
            if patient_count == 0:
                print(f"   🌱 Necesita población de datos")
                
                # Usar el comando populate_db pero con contexto específico
                from django.core.management import call_command
                try:
                    call_command('populate_db')
                    print(f"   ✅ Datos poblados exitosamente")
                except Exception as e:
                    print(f"   ❌ Error al poblar: {str(e)}")
            else:
                print(f"   ✅ Ya tiene datos")

def verify_final_state():
    """Verificar el estado final"""
    
    print(f"\n📊 Estado Final del Sistema")
    print("=" * 35)
    
    clinics = Clinic.objects.exclude(schema_name='public')
    
    for clinic in clinics:
        print(f"\n🏥 {clinic.name} ({clinic.schema_name}):")
        
        with schema_context(clinic.schema_name):
            # Contar todos los tipos de usuarios
            total_users = CustomUser.objects.count()
            patients = CustomUser.objects.filter(user_type='patient').count()
            professionals = CustomUser.objects.filter(user_type='professional').count()
            admins = CustomUser.objects.filter(user_type='admin').count()
            
            print(f"   👥 Total usuarios: {total_users}")
            print(f"   🏥 Pacientes: {patients}")
            print(f"   👨‍⚕️ Profesionales: {professionals}")
            print(f"   🔧 Administradores: {admins}")
            
            # Verificar admin específico
            admin = CustomUser.objects.filter(email='admin@gmail.com').first()
            if admin:
                print(f"   ✅ Admin creado: {admin.get_full_name()}")
            else:
                print(f"   ❌ Admin no encontrado")

if __name__ == "__main__":
    try:
        create_clinic_admins()
        populate_tenant_data()
        verify_final_state()
        
        print(f"\n🚀 ¡Proceso completado!")
        print(f"📝 Credenciales de admin para ambas clínicas:")
        print(f"   📧 Email: admin@gmail.com")
        print(f"   🔐 Contraseña: admin")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()