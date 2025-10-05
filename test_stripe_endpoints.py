#!/usr/bin/env python
"""
Script para probar los endpoints de Stripe
"""

import requests
import json

def test_stripe_endpoints():
    """Prueba todos los endpoints de Stripe"""
    
    base_url = "https://yolonda-unoverruled-pseudoemotionally.ngrok-free.dev"
    headers = {
        'ngrok-skip-browser-warning': 'true',
        'Content-Type': 'application/json'
    }
    
    print("🧪 PROBANDO ENDPOINTS DE STRIPE")
    print("=" * 50)
    
    # 1. Probar endpoint de clave pública
    print("\n1. Probando endpoint de clave pública:")
    try:
        response = requests.get(f"{base_url}/api/payments/stripe-public-key/", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Clave pública obtenida: {data.get('publishable_key', 'N/A')[:20]}...")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
    
    # 2. Probar endpoint de webhook (sin datos, solo verificar que responda)
    print("\n2. Probando endpoint de webhook (verificación de ruta):")
    try:
        response = requests.post(f"{base_url}/api/payments/stripe-webhook/", headers=headers, json={})
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:  # Esperamos 400 porque no enviamos datos válidos de Stripe
            print("   ✓ Webhook responde correctamente (400 es esperado sin datos de Stripe)")
        else:
            print(f"   ⚠️  Respuesta inesperada: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ PRUEBAS COMPLETADAS")
    print("\n📋 URLs para configurar en Stripe Dashboard:")
    print(f"   Webhook URL: {base_url}/api/payments/stripe-webhook/")
    print(f"   Eventos a escuchar: checkout.session.completed")

if __name__ == "__main__":
    test_stripe_endpoints()