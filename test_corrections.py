#!/usr/bin/env python3
"""
Script para probar las correcciones realizadas
"""
import requests
import time

def test_corrections():
    print("🔧 PROBANDO CORRECCIONES DEL SISTEMA")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # Esperar que el servidor esté listo
    print("⏳ Esperando que el servidor esté disponible...")
    time.sleep(2)
    
    tests = [
        {
            "name": "🏢 ADMIN PÚBLICO (corregido)",
            "url": f"{base_url}/admin/",
            "host": None,
            "description": "Admin personalizado sin django_admin_log"
        },
        {
            "name": "🏥 API BIENESTAR (corregido)",
            "url": f"{base_url}/api/professionals/",
            "host": "bienestar.localhost",
            "description": "API con rest_framework en TENANT_APPS"
        },
        {
            "name": "🏥 API MINDCARE (corregido)",
            "url": f"{base_url}/api/professionals/",
            "host": "mindcare.localhost",
            "description": "API con rest_framework en TENANT_APPS"
        }
    ]
    
    for test in tests:
        headers = {}
        if test["host"]:
            headers["Host"] = test["host"]
        
        try:
            response = requests.get(test["url"], headers=headers, timeout=10)
            
            print(f"\n{test['name']}")
            print(f"   🔗 URL: {test['url']}")
            print(f"   🌐 Host: {test['host'] or '127.0.0.1'}")
            print(f"   📊 Status: {response.status_code}")
            print(f"   📝 Fix: {test['description']}")
            
            if response.status_code == 200:
                if "admin" in test["url"]:
                    print("   ✅ ADMIN FUNCIONA - Error corregido")
                else:
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            print(f"   ✅ API FUNCIONA - {len(data)} profesionales")
                        else:
                            print("   ✅ API RESPONDE correctamente")
                    except:
                        print("   ✅ RESPUESTA VÁLIDA")
            elif response.status_code == 404:
                print("   ❌ TODAVÍA DA 404 - Revisar configuración")
            else:
                print(f"   ⚠️  Status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ ERROR: No se puede conectar al servidor")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("📋 CAMBIOS REALIZADOS:")
    print("✅ rest_framework agregado a TENANT_APPS")
    print("✅ Admin personalizado sin django_admin_log")
    print("✅ Admin site específico para público")
    print("=" * 50)

if __name__ == "__main__":
    test_corrections()