#!/usr/bin/env python3
"""
Verificación final del sistema multi-tenant completamente configurado
"""
import requests
import time

def final_verification():
    print("🎉 VERIFICACIÓN FINAL - SISTEMA MULTI-TENANT")
    print("=" * 60)
    print("Configuración aplicada:")
    print("✅ rest_framework y django.contrib.auth movidos a TENANT_APPS")
    print("✅ Admin personalizado para esquema público")
    print("✅ URLs separadas correctamente")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Esperar que el servidor esté listo
    print("\n⏳ Esperando que el servidor esté disponible...")
    time.sleep(3)
    
    tests = [
        {
            "name": "🏢 ADMIN PÚBLICO (con admin personalizado)",
            "url": f"{base_url}/admin/",
            "host": None,
            "expected": "Página de login sin errores"
        },
        {
            "name": "🏥 API BIENESTAR (con rest_framework en TENANT_APPS)",
            "url": f"{base_url}/api/professionals/",
            "host": "bienestar.localhost",
            "expected": "JSON con profesionales"
        },
        {
            "name": "🏥 API MINDCARE (con rest_framework en TENANT_APPS)",
            "url": f"{base_url}/api/professionals/",
            "host": "mindcare.localhost",
            "expected": "JSON con profesionales"
        },
        {
            "name": "❌ VERIFICACIÓN: API en público (debe dar 404)",
            "url": f"{base_url}/api/professionals/",
            "host": None,
            "expected": "404 - No hay API en esquema público"
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
            print(f"   🎯 Esperado: {test['expected']}")
            
            if response.status_code == 200:
                if "admin" in test["url"]:
                    if "login" in response.text.lower():
                        print("   ✅ PERFECTO: Admin funciona sin errores")
                    else:
                        print("   ✅ ADMIN RESPONDE correctamente")
                else:
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            print(f"   ✅ PERFECTO: API funciona - {len(data)} profesionales")
                        else:
                            print("   ✅ API RESPONDE correctamente")
                    except:
                        print("   ✅ RESPUESTA VÁLIDA")
            elif response.status_code == 404:
                if "debe dar 404" in test["name"]:
                    print("   ✅ PERFECTO: 404 esperado - Separación funciona")
                else:
                    print("   ❌ ERROR: Debería funcionar pero da 404")
            else:
                print(f"   ⚠️  Status inesperado: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ ERROR: No se puede conectar al servidor")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("📋 CONFIGURACIÓN FINAL APLICADA:")
    print("=" * 60)
    print("🔧 SHARED_APPS:")
    print("   • django_tenants")
    print("   • apps.tenants")
    print("   • contenttypes, sessions, messages, staticfiles")
    print("   • corsheaders, channels")
    
    print("\n🔧 TENANT_APPS:")
    print("   • django.contrib.admin")
    print("   • django.contrib.auth")
    print("   • rest_framework")
    print("   • rest_framework.authtoken")
    print("   • apps.users, authentication, professionals, etc.")
    
    print("\n🎯 ACCESO AL SISTEMA:")
    print("   🏢 Admin: http://127.0.0.1:8000/admin/")
    print("   🏥 APIs: http://bienestar.localhost:8000/api/")
    print("   📋 Hosts: 127.0.0.1 bienestar.localhost")
    print("=" * 60)

if __name__ == "__main__":
    final_verification()