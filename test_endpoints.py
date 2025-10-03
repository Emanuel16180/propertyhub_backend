#!/usr/bin/env python3
"""
Script para probar endpoints del sistema multi-tenant
"""
import requests

def test_endpoint(url, host_header=None):
    """Probar un endpoint con header Host opcional"""
    headers = {}
    if host_header:
        headers['Host'] = host_header
    
    try:
        response = requests.get(url, headers=headers)
        print(f"\n--- {host_header or 'localhost'} ---")
        print(f"URL: {url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"Resultados: {len(data)} items")
                    if data:
                        print(f"Primer item: {list(data[0].keys())}")
                else:
                    print(f"Respuesta: {data}")
            except:
                print(f"Contenido: {response.text[:200]}...")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error de conexión: {e}")

def main():
    base_url = "http://127.0.0.1:8000/api"
    
    print("🔍 Probando endpoints multi-tenant...")
    
    # Probar endpoint público (tenant público)
    test_endpoint(f"{base_url}/professionals/")
    
    # Probar endpoint en tenant bienestar
    test_endpoint(f"{base_url}/professionals/", "bienestar.localhost")
    test_endpoint(f"{base_url}/users/", "bienestar.localhost")
    test_endpoint(f"{base_url}/appointments/appointments/", "bienestar.localhost")

if __name__ == "__main__":
    main()