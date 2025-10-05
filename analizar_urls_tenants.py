#!/usr/bin/env python
"""
Script para verificar qué URLs están disponibles en cada tenant
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

from django.urls import get_resolver
from django.conf import settings

def analizar_urls_por_tenant():
    """Analiza qué URLs están disponibles en cada configuración"""
    
    print("🔍 ANÁLISIS DE URLs POR TENANT")
    print("=" * 60)
    
    # Analizar URLs públicas
    print("\n🌐 TENANT PÚBLICO (localhost, 127.0.0.1)")
    print("   Archivo: config/urls_public.py")
    print("   Propósito: Gestión de clínicas y webhooks")
    print("-" * 50)
    
    try:
        # Simular resolver de URLs públicas
        from config.urls_public import urlpatterns as public_patterns
        print("   URLs disponibles:")
        for pattern in public_patterns:
            if hasattr(pattern, 'pattern'):
                print(f"     • {pattern.pattern}")
            elif hasattr(pattern, 'url_patterns'):
                for sub_pattern in pattern.url_patterns:
                    print(f"     • {pattern.pattern}{sub_pattern.pattern}")
    except Exception as e:
        print(f"   ❌ Error analizando URLs públicas: {str(e)}")
    
    # Analizar URLs de tenants
    print(f"\n🏢 TENANTS DE CLÍNICAS (bienestar.localhost, mindcare.localhost)")
    print("   Archivo: config/urls.py")
    print("   Propósito: Funcionalidad completa de la clínica")
    print("-" * 50)
    
    try:
        from config.urls import urlpatterns as tenant_patterns
        print("   URLs disponibles:")
        for pattern in tenant_patterns:
            if hasattr(pattern, 'pattern'):
                print(f"     • {pattern.pattern}")
    except Exception as e:
        print(f"   ❌ Error analizando URLs de tenants: {str(e)}")
    
    # Comparación
    print(f"\n📊 COMPARACIÓN DE FUNCIONALIDADES")
    print("=" * 60)
    
    public_features = [
        "✅ Admin público (gestión clínicas)",
        "✅ Pagos/Stripe (webhooks)",
        "✅ Autenticación básica",
        "✅ Debug/pruebas",
        "❌ Gestión usuarios clínica",
        "❌ Citas",
        "❌ Profesionales",
        "❌ Historia clínica",
        "❌ Chat"
    ]
    
    tenant_features = [
        "❌ Admin público (no aplica)",
        "✅ Pagos/Stripe",
        "✅ Autenticación completa",
        "✅ Debug/pruebas",
        "✅ Gestión usuarios clínica",
        "✅ Citas",
        "✅ Profesionales", 
        "✅ Historia clínica",
        "✅ Chat"
    ]
    
    print("\n🌐 TENANT PÚBLICO:")
    for feature in public_features:
        print(f"   {feature}")
    
    print("\n🏢 TENANTS DE CLÍNICAS:")
    for feature in tenant_features:
        print(f"   {feature}")
    
    print(f"\n💡 EXPLICACIÓN DEL DISEÑO:")
    print("=" * 60)
    print("1. 🌐 TENANT PÚBLICO: Para administración general")
    print("   - Gestionar clínicas (crear/editar/eliminar)")
    print("   - Recibir webhooks de Stripe")
    print("   - Administración del sistema")
    print("")
    print("2. 🏢 TENANTS DE CLÍNICAS: Para operación diaria")
    print("   - Gestión completa de usuarios")
    print("   - Reserva y gestión de citas")
    print("   - Perfiles de profesionales")
    print("   - Historia clínica")
    print("   - Chat en tiempo real")
    print("   - Procesamiento de pagos")
    
    print(f"\n🔧 ACCESO CORRECTO:")
    print("=" * 60)
    print("• http://localhost:8000/admin/ → Admin público")
    print("• http://127.0.0.1:8000/admin/ → Admin público")
    print("• http://bienestar.localhost:8000/admin/ → Admin clínica Bienestar")
    print("• http://mindcare.localhost:8000/admin/ → Admin clínica MindCare")
    print("• http://bienestar.localhost:8000/api/auth/ → API auth clínica")
    print("• http://mindcare.localhost:8000/api/appointments/ → API citas clínica")

if __name__ == "__main__":
    analizar_urls_por_tenant()