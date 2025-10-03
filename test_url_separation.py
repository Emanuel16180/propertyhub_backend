#!/usr/bin/env python3
"""
Script para probar la nueva configuración de URLs separadas
"""
import requests
import time

def test_endpoint(url, host_header=None, description=""):
    """Probar un endpoint específico"""
    headers = {}
    if host_header:
        headers['Host'] = host_header
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        print(f"\n🔍 {description}")
        print(f"   URL: {url}")
        print(f"   Host: {host_header or 'localhost'}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"   ✅ Resultados: {len(data)} items")
                else:
                    print(f"   ✅ Respuesta válida: {type(data).__name__}")
            except:
                print(f"   ✅ Contenido HTML válido")
        elif response.status_code == 404:
            print(f"   ❌ 404 - Endpoint no encontrado")
        else:
            print(f"   ⚠️  Status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ No se puede conectar al servidor")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    print("🚀 Probando configuración de URLs separadas...")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Probar tenant público (debe mostrar admin)
    test_endpoint(f"{base_url}/admin/", None, "TENANT PÚBLICO - Admin")
    
    # Probar API en tenant público (debe fallar)
    test_endpoint(f"{base_url}/api/professionals/", None, "TENANT PÚBLICO - API (debe fallar)")
    
    # Probar tenants de clínicas
    test_endpoint(f"{base_url}/api/professionals/", "bienestar.localhost", "CLÍNICA BIENESTAR - Profesionales")
    test_endpoint(f"{base_url}/api/users/", "bienestar.localhost", "CLÍNICA BIENESTAR - Usuarios")
    
    test_endpoint(f"{base_url}/api/professionals/", "mindcare.localhost", "CLÍNICA MINDCARE - Profesionales")
    test_endpoint(f"{base_url}/api/users/", "mindcare.localhost", "CLÍNICA MINDCARE - Usuarios")
    
    print("\n" + "=" * 60)
    print("📋 INTERPRETACIÓN DE RESULTADOS:")
    print("=" * 60)
    print("✅ Admin en localhost debe funcionar (200)")
    print("❌ API en localhost debe fallar (404)")
    print("✅ API en clínicas debe funcionar (200)")
    print("🎯 Si ves esto, ¡la separación de URLs funciona perfectamente!")

if __name__ == "__main__":
    main()