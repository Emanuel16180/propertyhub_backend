#!/usr/bin/env python
"""
Prueba simplificada del sistema de pagos con Stripe
Se enfoca en probar endpoints y conectividad
"""

import requests
import json
import stripe
import os
from decouple import config

def prueba_sistema_stripe():
    """Prueba completa del sistema de Stripe"""
    
    print("🚀 PRUEBA COMPLETA DEL SISTEMA DE PAGOS STRIPE")
    print("=" * 70)
    
    # Configuración
    base_url = "https://yolonda-unoverruled-pseudoemotionally.ngrok-free.dev"
    headers = {
        'ngrok-skip-browser-warning': 'true',
        'Content-Type': 'application/json',
        'User-Agent': 'Test-Script/1.0'
    }
    
    # Configurar Stripe
    stripe.api_key = config("STRIPE_SECRET_KEY")
    
    resultados = {
        'stripe_conexion': False,
        'endpoint_clave_publica': False,
        'endpoint_webhook': False,
        'webhooks_configurados': False,
        'ngrok_funcionando': False
    }
    
    # 1. Verificar conexión con Stripe
    print("\n1. 🔗 VERIFICANDO CONEXIÓN CON STRIPE")
    print("-" * 50)
    
    try:
        balance = stripe.Balance.retrieve()
        print(f"   ✅ Conectado a Stripe exitosamente")
        print(f"   💰 Balance disponible: {balance.available[0].amount/100} {balance.available[0].currency.upper()}")
        print(f"   🏦 Balance pendiente: {balance.pending[0].amount/100} {balance.pending[0].currency.upper()}")
        resultados['stripe_conexion'] = True
    except Exception as e:
        print(f"   ❌ Error de conexión con Stripe: {str(e)}")
    
    # 2. Verificar endpoint de clave pública
    print("\n2. 🔑 VERIFICANDO ENDPOINT DE CLAVE PÚBLICA")
    print("-" * 50)
    
    try:
        response = requests.get(f"{base_url}/api/payments/stripe-public-key/", headers=headers, timeout=10)
        print(f"   📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            public_key = data.get('publicKey', '')
            print(f"   ✅ Clave pública obtenida exitosamente")
            print(f"   🔑 Clave: {public_key[:20]}...")
            print(f"   📏 Longitud: {len(public_key)} caracteres")
            resultados['endpoint_clave_publica'] = True
        else:
            print(f"   ❌ Error obteniendo clave pública")
            print(f"   📄 Respuesta: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
    
    # 3. Verificar endpoint de webhook
    print("\n3. 🪝 VERIFICANDO ENDPOINT DE WEBHOOK")
    print("-" * 50)
    
    try:
        response = requests.post(f"{base_url}/api/payments/stripe-webhook/", 
                               headers=headers, 
                               json={}, 
                               timeout=10)
        print(f"   📡 Status Code: {response.status_code}")
        
        if response.status_code == 400:
            print(f"   ✅ Webhook responde correctamente")
            print(f"   💡 Error 400 es esperado (sin datos válidos de Stripe)")
            resultados['endpoint_webhook'] = True
        else:
            print(f"   ⚠️  Status inesperado: {response.status_code}")
            print(f"   📄 Respuesta: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
    
    # 4. Verificar ngrok
    print("\n4. 🌐 VERIFICANDO CONFIGURACIÓN DE NGROK")
    print("-" * 50)
    
    try:
        # Probar que ngrok responde
        response = requests.get(f"{base_url}/api/payments/stripe-public-key/", 
                               headers=headers, 
                               timeout=10)
        if response.status_code in [200, 400, 401, 404]:  # Cualquier respuesta válida
            print(f"   ✅ Ngrok funcionando correctamente")
            print(f"   🌍 URL accesible: {base_url}")
            resultados['ngrok_funcionando'] = True
        else:
            print(f"   ⚠️  Respuesta inesperada de ngrok")
            
    except Exception as e:
        print(f"   ❌ Error conectando a ngrok: {str(e)}")
    
    # 5. Verificar webhooks en Stripe Dashboard
    print("\n5. 🔗 VERIFICANDO WEBHOOKS EN STRIPE DASHBOARD")
    print("-" * 50)
    
    try:
        webhooks = stripe.WebhookEndpoint.list()
        print(f"   📊 Total webhooks: {len(webhooks.data)}")
        
        webhook_url_correcta = f"{base_url}/api/payments/stripe-webhook/"
        webhook_encontrado = False
        
        for i, webhook in enumerate(webhooks.data):
            print(f"\n   🔗 Webhook #{i+1}:")
            print(f"      ID: {webhook.id}")
            print(f"      URL: {webhook.url}")
            print(f"      Status: {webhook.status}")
            print(f"      Eventos: {', '.join(webhook.enabled_events)}")
            
            if webhook.url == webhook_url_correcta:
                webhook_encontrado = True
                print(f"      ✅ ¡ESTE ES EL WEBHOOK CORRECTO!")
        
        if webhook_encontrado:
            print(f"\n   ✅ Webhook configurado correctamente")
            resultados['webhooks_configurados'] = True
        else:
            print(f"\n   ⚠️  Webhook con URL correcta no encontrado")
            
    except Exception as e:
        print(f"   ❌ Error verificando webhooks: {str(e)}")
    
    # 6. Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 70)
    
    total_pruebas = len(resultados)
    pruebas_exitosas = sum(resultados.values())
    
    for componente, estado in resultados.items():
        icono = "✅" if estado else "❌"
        nombre = componente.replace('_', ' ').title()
        print(f"   {icono} {nombre}")
    
    print(f"\n📈 SCORE: {pruebas_exitosas}/{total_pruebas} ({(pruebas_exitosas/total_pruebas)*100:.1f}%)")
    
    if pruebas_exitosas == total_pruebas:
        print("\n🎉 ¡SISTEMA 100% OPERATIVO!")
        print("   Ready para integración con frontend 🚀")
    elif pruebas_exitosas >= 3:
        print("\n✅ Sistema mayormente funcional")
        print("   Listo para desarrollo frontend 👍")
    else:
        print("\n⚠️ Algunos componentes necesitan atención")
    
    # 7. Información para el frontend
    print("\n" + "=" * 70)
    print("📋 INFORMACIÓN PARA EL FRONTEND")
    print("=" * 70)
    
    print(f"🌐 Base URL: {base_url}")
    print(f"🔑 Endpoint clave pública: {base_url}/api/payments/stripe-public-key/")
    print(f"💳 Endpoint crear pago: {base_url}/api/payments/create-checkout-session/")
    print(f"📊 Endpoint estado pago: {base_url}/api/payments/payment-status/<id>/")
    print(f"🔧 Método autenticación: Token Bearer en headers")
    
    return resultados

if __name__ == "__main__":
    prueba_sistema_stripe()