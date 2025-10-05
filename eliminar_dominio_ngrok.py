#!/usr/bin/env python
"""
Script para eliminar el dominio de ngrok del tenant bienestar
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django_tenants.utils import get_tenant_model

def eliminar_dominio_ngrok():
    """Elimina el dominio de ngrok del tenant bienestar"""
    
    print("🗑️ ELIMINANDO DOMINIO NGROK DEL TENANT BIENESTAR")
    print("=" * 60)
    
    try:
        Tenant = get_tenant_model()
        
        # Buscar el tenant bienestar
        bienestar_tenant = Tenant.objects.get(schema_name='bienestar')
        
        # Dominio de ngrok a eliminar
        ngrok_domain = 'yolonda-unoverruled-pseudoemotionally.ngrok-free.dev'
        
        # Buscar y eliminar el dominio de ngrok
        dominios_ngrok = bienestar_tenant.domains.filter(domain=ngrok_domain)
        
        if dominios_ngrok.exists():
            for dominio in dominios_ngrok:
                print(f"   🗑️ Eliminando dominio: {dominio.domain}")
                dominio.delete()
            print(f"   ✅ Dominio de ngrok eliminado exitosamente")
        else:
            print(f"   ⚠️ No se encontró el dominio de ngrok en el tenant bienestar")
        
        # Verificar dominios restantes
        print(f"\n📋 Dominios restantes en bienestar:")
        for dominio in bienestar_tenant.domains.all():
            print(f"   🌐 {dominio.domain} (Principal: {dominio.is_primary})")
        
        print("\n" + "=" * 60)
        print("✅ OPERACIÓN COMPLETADA")
        print("Ahora intenta acceder a:")
        print("   • http://bienestar.localhost:8000/admin/")
        print("   • http://mindcare.localhost:8000/admin/")
        print("   • http://localhost:8000/admin/")
        
    except Exception as e:
        print(f"❌ Error eliminando dominio: {str(e)}")

if __name__ == "__main__":
    eliminar_dominio_ngrok()