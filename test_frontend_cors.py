#!/usr/bin/env python3
"""
Script para probar la conectividad CORS desde diferentes dominios
"""
import requests
import json

def test_cors_endpoint(url, origin):
    """Prueba un endpoint con un origen específico"""
    headers = {
        'Origin': origin,
        'Content-Type': 'application/json',
    }
    
    # Primero hacer OPTIONS request (preflight)
    options_response = requests.options(url, headers=headers)
    print(f"\n=== PROBANDO {origin} → {url} ===")
    print(f"OPTIONS Status: {options_response.status_code}")
    print(f"Access-Control-Allow-Origin: {options_response.headers.get('Access-Control-Allow-Origin', 'No presente')}")
    print(f"Access-Control-Allow-Methods: {options_response.headers.get('Access-Control-Allow-Methods', 'No presente')}")
    print(f"Access-Control-Allow-Headers: {options_response.headers.get('Access-Control-Allow-Headers', 'No presente')}")
    
    # Luego hacer POST request real
    try:
        post_data = {'email': 'admin2@gmail.com', 'password': 'admin'}
        post_response = requests.post(url, json=post_data, headers=headers)
        print(f"POST Status: {post_response.status_code}")
        if post_response.status_code == 200:
            print("✅ LOGIN EXITOSO")
            response_data = post_response.json()
            print(f"Token: {response_data.get('token', 'No presente')[:20]}...")
        else:
            print(f"❌ ERROR: {post_response.text}")
    except Exception as e:
        print(f"❌ EXCEPCIÓN: {e}")

if __name__ == "__main__":
    # URLs a probar
    urls = [
        "http://bienestar.localhost:8000/api/auth/login/",
        "http://mindcare.localhost:8000/api/auth/login/",
    ]
    
    # Orígenes a probar (simulando el frontend)
    origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://bienestar.localhost:5174",
        "http://mindcare.localhost:5174",
        "http://bienestar.localhost:3000",
        "http://mindcare.localhost:3000",
    ]
    
    print("🧪 PROBANDO CONECTIVIDAD CORS PARA FRONTEND")
    print("=" * 60)
    
    for url in urls:
        for origin in origins:
            test_cors_endpoint(url, origin)
    
    print("\n" + "=" * 60)
    print("✨ PRUEBAS COMPLETADAS")