#!/usr/bin/env python
"""
Test específico para verificar el funcionamiento de subdominios después del fix
"""

import requests
import time

def test_dominios_post_fix():
    """Prueba específica después de quitar el middleware problemático"""
    
    print("🔧 PROBANDO DOMINIOS DESPUÉS DEL FIX DE MIDDLEWARE")
    print("=" * 60)
    
    dominios_test = [
        {
            'url': 'http://localhost:8000/admin/',
            'descripcion': 'Admin público (tenant público)',
            'esperado': 'Debería funcionar - Admin para gestionar clínicas'
        },
        {
            'url': 'http://bienestar.localhost:8000/admin/',
            'descripcion': 'Admin de clínica Bienestar',
            'esperado': 'Debería funcionar - Admin específico de clínica'
        },
        {
            'url': 'http://mindcare.localhost:8000/admin/',
            'descripcion': 'Admin de clínica MindCare',
            'esperado': 'Debería funcionar - Admin específico de clínica'
        },
        {
            'url': 'http://bienestar.localhost:8000/api/auth/',
            'descripcion': 'API de auth en Bienestar',
            'esperado': 'Debería responder - Endpoints de la clínica'
        }
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    resultados = {}
    
    for test in dominios_test:
        print(f"\n🔍 Probando: {test['descripcion']}")
        print(f"   URL: {test['url']}")
        print(f"   Esperado: {test['esperado']}")
        
        try:
            response = requests.get(test['url'], headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ Status: {response.status_code} - FUNCIONANDO")
                resultados[test['url']] = 'FUNCIONANDO'
            elif response.status_code in [301, 302]:
                print(f"   🔄 Status: {response.status_code} - REDIRECCIÓN (normal)")
                resultados[test['url']] = 'REDIRIGIENDO'
            elif response.status_code == 404:
                print(f"   ❌ Status: {response.status_code} - NO ENCONTRADO (problema)")
                resultados[test['url']] = 'ERROR_404'
            elif response.status_code == 403:
                print(f"   🔒 Status: {response.status_code} - PROHIBIDO (normal si no logueado)")
                resultados[test['url']] = 'PROHIBIDO'
            else:
                print(f"   ⚠️  Status: {response.status_code} - OTRO")
                resultados[test['url']] = f'STATUS_{response.status_code}'
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ ERROR: No se puede conectar al servidor")
            resultados[test['url']] = 'NO_CONEXION'
        except requests.exceptions.Timeout:
            print(f"   ⏰ ERROR: Timeout")
            resultados[test['url']] = 'TIMEOUT'
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            resultados[test['url']] = 'ERROR_GENERAL'
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    funcionando = sum(1 for v in resultados.values() if v in ['FUNCIONANDO', 'REDIRIGIENDO', 'PROHIBIDO'])
    total = len(resultados)
    
    print(f"✅ Funcionando correctamente: {funcionando}/{total}")
    
    if funcionando == total:
        print("\n🎉 ¡TODOS LOS DOMINIOS FUNCIONAN!")
        print("El problema del middleware ha sido solucionado.")
    elif funcionando > total // 2:
        print("\n✅ La mayoría funciona correctamente")
        print("Es probable que algunos errores sean normales (permisos, etc.)")
    else:
        print("\n⚠️ Algunos dominios aún tienen problemas")
        print("Puede que necesites reiniciar el navegador o limpiar caché DNS")
    
    # Instrucciones específicas
    if any(v == 'NO_CONEXION' for v in resultados.values()):
        print("\n🔧 SOLUCIONES SUGERIDAS:")
        print("1. Verificar que el servidor Django esté corriendo")
        print("2. Limpiar caché DNS: ipconfig /flushdns")
        print("3. Reiniciar navegador completamente")
        print("4. Verificar archivo hosts")
    
    return resultados

if __name__ == "__main__":
    test_dominios_post_fix()