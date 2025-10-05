#!/usr/bin/env python
"""
Script para agregar el dominio de ngrok al tenant bienestar
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
from django_tenants.models import DomainMixin

def agregar_dominio_ngrok():
    """Agrega el dominio de ngrok al tenant bienestar"""
    
    print("🌐 AGREGANDO DOMINIO NGROK AL TENANT BIENESTAR")
    print("=" * 50)
    
    try:
        Tenant = get_tenant_model()
        
        # Buscar el tenant bienestar
        bienestar_tenant = Tenant.objects.get(schema_name='bienestar')
        
        # Dominio de ngrok
        ngrok_domain = 'yolonda-unoverruled-pseudoemotionally.ngrok-free.dev'
        
        # Verificar si ya existe en los dominios del tenant
        existing_domain = bienestar_tenant.domains.filter(domain=ngrok_domain).first()
        if existing_domain:
            print(f"   ⚠️  El dominio {ngrok_domain} ya existe")
            print(f"   📋 Tenant actual: {existing_domain.tenant.schema_name}")
            return
        
        # Crear el nuevo dominio usando el modelo de dominios del tenant
        new_domain = bienestar_tenant.domains.create(
            domain=ngrok_domain,
            is_primary=False  # No es el dominio principal
        )
        
        print(f"   ✅ Dominio agregado exitosamente")
        print(f"   🌐 Dominio: {new_domain.domain}")
        print(f"   📋 Tenant: {new_domain.tenant.schema_name}")
        print(f"   🏠 Es principal: {new_domain.is_primary}")
        
        print("\n" + "=" * 50)
        print("🚀 CONFIGURACIÓN COMPLETADA")
        print(f"\n📋 URLs para Stripe:")
        print(f"   Webhook: https://{ngrok_domain}/api/payments/stripe-webhook/")
        print(f"   Clave pública: https://{ngrok_domain}/api/payments/stripe-public-key/")
        
    except Exception as e:
        print(f"❌ Error al agregar dominio: {str(e)}")

if __name__ == "__main__":
    agregar_dominio_ngrok()