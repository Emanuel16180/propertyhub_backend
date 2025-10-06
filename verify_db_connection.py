#!/usr/bin/env python
"""
Verificar credenciales de la base de datos
"""

import os
import sys
import django

# Configurar Django
sys.path.append('c:/Users/asus/Documents/psico_admin_sp1_despliegue')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.db import connection

def verify_django_connection():
    """Verificar que Django puede conectarse a la base de datos"""
    
    print("🔧 VERIFICANDO CONEXIÓN DE DJANGO")
    print("=" * 40)
    
    try:
        # Intentar una consulta simple
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database(), current_user, version();")
            result = cursor.fetchone()
            
        print(f"✅ Django se conecta exitosamente")
        print(f"📊 Base de datos: {result[0]}")
        print(f"👤 Usuario: {result[1]}")
        print(f"🐘 Versión PostgreSQL: {result[2][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Django NO puede conectarse: {e}")
        return False

def show_database_config():
    """Mostrar configuración de la base de datos"""
    
    print(f"\n📋 CONFIGURACIÓN DE BASE DE DATOS")
    print("=" * 40)
    
    db_settings = settings.DATABASES['default']
    
    print(f"🔧 Configuración actual:")
    for key, value in db_settings.items():
        if key == 'PASSWORD':
            # Mostrar solo los primeros y últimos caracteres
            if value:
                masked = value[:2] + '*' * (len(value) - 4) + value[-2:] if len(value) > 4 else '***'
                print(f"   {key}: {masked}")
            else:
                print(f"   {key}: (vacía)")
        else:
            print(f"   {key}: {value}")

def suggest_solutions():
    """Sugerir soluciones basadas en los resultados"""
    
    print(f"\n💡 SOLUCIONES SUGERIDAS")
    print("=" * 25)
    
    print(f"🔧 Si Django funciona pero pg_dump no:")
    print(f"   1. El problema es que pg_dump usa credenciales diferentes")
    print(f"   2. Django podría estar usando autenticación 'trust' o 'peer'")
    print(f"   3. Necesitamos configurar pg_hba.conf para pg_dump")
    
    print(f"\n🛠️ Pasos para arreglar:")
    print(f"   1. Encontrar archivo pg_hba.conf")
    print(f"   2. Añadir línea: host all postgres 127.0.0.1/32 md5")
    print(f"   3. O cambiar método de auth para localhost")
    print(f"   4. Reiniciar servicio PostgreSQL")
    
    print(f"\n⚡ Solución rápida alternativa:")
    print(f"   - Usar un método de backup que NO dependa de pg_dump")
    print(f"   - Como Django dumpdata/loaddata (ya implementado)")

if __name__ == "__main__":
    django_works = verify_django_connection()
    show_database_config()
    suggest_solutions()
    
    if django_works:
        print(f"\n🎯 CONCLUSIÓN: El problema está en pg_dump, no en Django")
        print(f"   Django se conecta → Base de datos funciona")
        print(f"   pg_dump no se conecta → Problema de autenticación externa")
    else:
        print(f"\n🎯 CONCLUSIÓN: Problema general de base de datos")
        print(f"   Django tampoco se conecta → Verificar servicio PostgreSQL")