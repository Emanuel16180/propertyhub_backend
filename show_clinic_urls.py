#!/usr/bin/env python3
"""
Script para mostrar las URLs de las diferentes clínicas
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tenants.models import Clinic, Domain

def main():
    print("🏥 CLÍNICAS DISPONIBLES PARA PROBAR:")
    print("=" * 50)
    
    for clinic in Clinic.objects.all():
        domain = Domain.objects.filter(tenant=clinic).first()
        
        print(f"\n🏢 {clinic.name}")
        print(f"   📝 Schema: {clinic.schema_name}")
        print(f"   🌐 URL Base: http://{domain.domain}:8000")
        print(f"   🔗 API: http://{domain.domain}:8000/api/")
        
        # Mostrar algunos endpoints específicos
        if clinic.schema_name != 'public':
            print(f"   📊 Endpoints principales:")
            print(f"      • Profesionales: http://{domain.domain}:8000/api/professionals/")
            print(f"      • Usuarios: http://{domain.domain}:8000/api/users/")
            print(f"      • Citas: http://{domain.domain}:8000/api/appointments/appointments/")
            print(f"      • Login: http://{domain.domain}:8000/api/auth/login/")
    
    print("\n" + "=" * 50)
    print("📋 INSTRUCCIONES PARA PROBAR:")
    print("=" * 50)
    print("1. Asegúrate de tener el archivo hosts configurado:")
    print("   Archivo: C:\\Windows\\System32\\drivers\\etc\\hosts")
    print("   Línea: 127.0.0.1 bienestar.localhost")
    print("\n2. Inicia el servidor:")
    print("   python manage.py runserver")
    print("\n3. Abre tu navegador y visita las URLs mostradas arriba")

if __name__ == "__main__":
    main()