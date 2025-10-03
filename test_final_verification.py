#!/usr/bin/env python3
"""
Verificación final completa del sistema multi-tenant
"""
import requests
import time

def test_connectivity():
    print("🔥 VERIFICACIÓN FINAL - SISTEMA MULTI-TENANT")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    tests = [
        {
            "name": "🏢 ADMIN PÚBLICO",
            "url": f"{base_url}/admin/",
            "host": None,
            "description": "Página de login del admin"
        },
        {
            "name": "🏥 API BIENESTAR",
            "url": f"{base_url}/api/professionals/",
            "host": "bienestar.localhost",
            "description": "JSON con profesionales"
        },
        {
            "name": "🏥 API MINDCARE",
            "url": f"{base_url}/api/professionals/",
            "host": "mindcare.localhost",
            "description": "JSON con profesionales"
        },
        {
            "name": "❌ API EN PÚBLICO (debe fallar)",
            "url": f"{base_url}/api/professionals/",
            "host": None,
            "description": "404 esperado"
        }
    ]
    
    for test in tests:
        headers = {}
        if test["host"]:
            headers["Host"] = test["host"]
        
        try:
            response = requests.get(test["url"], headers=headers, timeout=5)
            
            print(f"\n{test['name']}")
            print(f"   🔗 URL: {test['url']}")
            print(f"   🌐 Host: {test['host'] or '127.0.0.1'}")
            print(f"   📊 Status: {response.status_code}")
            print(f"   📝 Esperado: {test['description']}")
            
            if response.status_code == 200:
                if "admin" in test["url"]:
                    print("   ✅ ADMIN ACCESIBLE")
                else:
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            print(f"   ✅ API FUNCIONA - {len(data)} profesionales")
                        else:
                            print("   ✅ API RESPONDE")
                    except:
                        print("   ✅ CONTENIDO VÁLIDO")
            elif response.status_code == 404:
                if "debe fallar" in test["name"]:
                    print("   ✅ 404 ESPERADO - Separación funciona")
                else:
                    print("   ⚠️  404 - Verificar configuración")
            else:
                print(f"   ⚠️  Status inesperado: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ ERROR: Servidor no disponible")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")

if __name__ == "__main__":
    test_connectivity()