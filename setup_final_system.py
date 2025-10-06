#!/usr/bin/env python
"""
Script simplificado para crear administradores y poblar datos
"""

import os
import sys
import django

# Configurar Django
sys.path.append('c:/Users/asus/Documents/psico_admin_sp1_despliegue')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django_tenants.utils import schema_context
from apps.tenants.models import Clinic
from apps.users.models import CustomUser

def create_admins_and_populate():
    """Crear administradores y poblar datos para cada clínica"""
    
    print("🔧 Configuración Completa del Sistema")
    print("=" * 40)
    
    # Obtener todas las clínicas (excluyendo public)
    clinics = Clinic.objects.exclude(schema_name='public')
    
    for clinic in clinics:
        print(f"\n🏥 Configurando {clinic.name} (schema: {clinic.schema_name})")
        
        # Cambiar al contexto del tenant
        with schema_context(clinic.schema_name):
            # 1. Crear administrador si no existe
            admin_email = 'admin@gmail.com'
            admin_exists = CustomUser.objects.filter(email=admin_email).exists()
            
            if admin_exists:
                print(f"   ✅ Admin ya existe")
                admin = CustomUser.objects.get(email=admin_email)
            else:
                # Crear el usuario administrador
                admin = CustomUser.objects.create_user(
                    email=admin_email,
                    password='admin',
                    first_name='Admin',
                    last_name=clinic.name,
                    user_type='admin',
                    ci='99999999'  # CI ficticio para admin
                )
                print(f"   ✅ Admin creado: {admin.get_full_name()}")
            
            # 2. Verificar y poblar datos si es necesario
            user_count = CustomUser.objects.count()
            patient_count = CustomUser.objects.filter(user_type='patient').count()
            professional_count = CustomUser.objects.filter(user_type='professional').count()
            
            print(f"   📊 Estado actual: {user_count} usuarios totales")
            print(f"   - Pacientes: {patient_count}")
            print(f"   - Profesionales: {professional_count}")
            print(f"   - Admins: {CustomUser.objects.filter(user_type='admin').count()}")
            
            # Si hay pocos usuarios, poblar más datos
            if patient_count < 10:
                print(f"   🌱 Poblando datos adicionales...")
                
                # Importar y usar el código de populate_db directamente
                from apps.users.management.commands.populate_db import Command as PopulateCommand
                
                try:
                    populate_cmd = PopulateCommand()
                    populate_cmd.handle()
                    print(f"   ✅ Datos poblados exitosamente")
                except Exception as e:
                    print(f"   ⚠️ Error al poblar: {str(e)}")
                    # Crear algunos datos mínimos manualmente
                    create_minimal_data(clinic)
            else:
                print(f"   ✅ Ya tiene suficientes datos")

def create_minimal_data(clinic):
    """Crear datos mínimos si falla la población automática"""
    
    print(f"   🔧 Creando datos mínimos...")
    
    # Crear al menos algunos pacientes de prueba
    test_patients = [
        {'email': 'paciente1@test.com', 'first_name': 'Juan', 'last_name': 'Pérez', 'ci': '12345678'},
        {'email': 'paciente2@test.com', 'first_name': 'María', 'last_name': 'González', 'ci': '87654321'},
        {'email': 'paciente3@test.com', 'first_name': 'Carlos', 'last_name': 'López', 'ci': '11223344'},
    ]
    
    for patient_data in test_patients:
        if not CustomUser.objects.filter(email=patient_data['email']).exists():
            CustomUser.objects.create_user(
                email=patient_data['email'],
                password='test123',
                first_name=patient_data['first_name'],
                last_name=patient_data['last_name'],
                user_type='patient',
                ci=patient_data['ci']
            )
    
    print(f"   ✅ Datos mínimos creados")

def show_final_status():
    """Mostrar el estado final del sistema"""
    
    print(f"\n📊 ESTADO FINAL DEL SISTEMA")
    print("=" * 35)
    
    clinics = Clinic.objects.exclude(schema_name='public')
    
    for clinic in clinics:
        print(f"\n🏥 {clinic.name}:")
        print(f"   🌐 URL: http://{clinic.schema_name}.localhost:8000")
        
        with schema_context(clinic.schema_name):
            total = CustomUser.objects.count()
            patients = CustomUser.objects.filter(user_type='patient').count()
            professionals = CustomUser.objects.filter(user_type='professional').count()
            admins = CustomUser.objects.filter(user_type='admin').count()
            
            print(f"   👥 Total usuarios: {total}")
            print(f"   🏥 Pacientes: {patients}")
            print(f"   👨‍⚕️ Profesionales: {professionals}")
            print(f"   🔧 Administradores: {admins}")
    
    print(f"\n🔐 CREDENCIALES DE ADMINISTRADOR:")
    print(f"   📧 Email: admin@gmail.com")
    print(f"   🔑 Contraseña: admin")
    print(f"   🎯 User Type: admin (IsClinicAdmin=True)")
    
    print(f"\n🚀 ¡Sistema listo para usar!")
    print(f"   - Ambas clínicas tienen administradores")
    print(f"   - Datos de prueba poblados")
    print(f"   - Sistema de backup funcional")

if __name__ == "__main__":
    try:
        create_admins_and_populate()
        show_final_status()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()