#!/usr/bin/env python
"""
Script para agregar 127.0.0.1 al tenant público
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

def agregar_127_al_tenant_publico():
    """Agrega 127.0.0.1 al tenant público para evitar errores"""
    
    print("🔧 AGREGANDO 127.0.0.1 AL TENANT PÚBLICO")
    print("=" * 50)
    
    try:
        Tenant = get_tenant_model()
        
        # Buscar el tenant público
        public_tenant = Tenant.objects.get(schema_name='public')
        
        # Verificar si ya existe el dominio 127.0.0.1
        existing_domain = public_tenant.domains.filter(domain='127.0.0.1').first()
        if existing_domain:
            print(f"   ⚠️ El dominio 127.0.0.1 ya existe")
            return
        
        # Crear el nuevo dominio
        new_domain = public_tenant.domains.create(
            domain='127.0.0.1',
            is_primary=False  # No es el dominio principal
        )
        
        print(f"   ✅ Dominio 127.0.0.1 agregado al tenant público")
        
        # Mostrar todos los dominios del tenant público
        print(f"\n📋 Dominios del tenant público:")
        for domain in public_tenant.domains.all():
            print(f"   🌐 {domain.domain} ({'Principal' if domain.is_primary else 'Secundario'})")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    agregar_127_al_tenant_publico()