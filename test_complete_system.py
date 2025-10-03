#!/usr/bin/env python3
"""
Script para probar el sistema multi-tenant sin cerrar el servidor
"""
import subprocess
import time
import requests
import threading
import sys

def start_server():
    """Iniciar el servidor Django en un hilo separado"""
    try:
        subprocess.run([sys.executable, "manage.py", "runserver"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Error al iniciar el servidor")

def test_endpoints():
    """Probar endpoints después de que el servidor esté listo"""
    print("⏳ Esperando que el servidor esté listo...")
    time.sleep(3)
    
    base_url = "http://127.0.0.1:8000/api"
    
    print("\n🔍 Probando endpoints multi-tenant...")
    
    tests = [
        ("Public tenant", f"{base_url}/professionals/", None),
        ("Bienestar - Profesionales", f"{base_url}/professionals/", "bienestar.localhost"),
        ("Bienestar - Usuarios", f"{base_url}/users/", "bienestar.localhost"),
        ("Bienestar - Citas", f"{base_url}/appointments/appointments/", "bienestar.localhost"),
    ]
    
    for test_name, url, host in tests:
        headers = {}
        if host:
            headers['Host'] = host
            
        try:
            response = requests.get(url, headers=headers, timeout=5)
            print(f"\n--- {test_name} ---")
            print(f"URL: {url}")
            print(f"Host: {host or 'localhost'}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"✅ Resultados: {len(data)} items")
                        if data and isinstance(data[0], dict):
                            print(f"📝 Campos: {list(data[0].keys())}")
                    else:
                        print(f"✅ Respuesta: {type(data).__name__}")
                except:
                    print(f"✅ Contenido HTML recibido")
            elif response.status_code == 404:
                if "No tenant for hostname" in response.text:
                    print("⚠️  Tenant no encontrado (esperado para localhost)")
                else:
                    print("❌ 404 - Endpoint no encontrado")
            else:
                print(f"❌ Error {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {test_name}: No se puede conectar al servidor")
        except Exception as e:
            print(f"❌ {test_name}: Error {e}")

def main():
    print("🚀 Iniciando pruebas del sistema multi-tenant...")
    
    # Iniciar servidor en hilo separado
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Hacer pruebas
    test_endpoints()
    
    print("\n" + "="*50)
    print("📋 RESUMEN DE CONFIGURACIÓN REQUERIDA:")
    print("="*50)
    print("Para probar completamente el sistema, necesitas:")
    print("1. Configurar el archivo hosts:")
    print("   Archivo: C:\\Windows\\System32\\drivers\\etc\\hosts")
    print("   Línea: 127.0.0.1 bienestar.localhost")
    print("2. Ejecutar como Administrador:")
    print("   Add-Content -Path \"C:\\Windows\\System32\\drivers\\etc\\hosts\" -Value \"`n127.0.0.1 bienestar.localhost\"")
    print("3. Luego ejecutar este script nuevamente")
    print("="*50)

if __name__ == "__main__":
    main()