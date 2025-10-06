#!/usr/bin/env python
"""
Script para probar diferentes configuraciones de host para pg_dump
"""

import subprocess
import os
from django.conf import settings
import sys
import django

# Configurar Django
sys.path.append('c:/Users/asus/Documents/psico_admin_sp1_despliegue')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_different_hosts():
    """Probar pg_dump con diferentes configuraciones de host"""
    
    print("🔧 PROBANDO DIFERENTES CONFIGURACIONES DE HOST")
    print("=" * 50)
    
    db_settings = settings.DATABASES['default']
    schema_name = "bienestar"
    
    print(f"📊 Configuración actual de Django:")
    print(f"   - Base de datos: {db_settings['NAME']}")
    print(f"   - Host original: {db_settings['HOST']}")
    print(f"   - Puerto: {db_settings['PORT']}")
    print(f"   - Usuario: {db_settings['USER']}")
    
    # Lista de hosts alternativos para probar
    hosts_to_try = [
        "127.0.0.1",      # IP local en lugar de localhost
        "localhost",      # Original
        "::1",            # IPv6 localhost
        "",               # Host vacío (usa socket local)
    ]
    
    env = {'PGPASSWORD': db_settings['PASSWORD']}
    
    for host in hosts_to_try:
        print(f"\n🔍 Probando con host: '{host}'")
        
        # Construir comando base
        command = [
            'pg_dump',
            '--dbname', db_settings['NAME'],
            '--port', str(db_settings['PORT']),
            '--username', db_settings['USER'],
            '--schema', schema_name,
            '--format', 'p',
            '--no-owner',
            '--no-privileges'
        ]
        
        # Añadir host solo si no está vacío
        if host:
            command.extend(['--host', host])
        
        print(f"   Comando: {' '.join(command)}")
        
        try:
            # Ejecutar con timeout para evitar cuelgues
            process = subprocess.run(
                command,
                capture_output=True,
                timeout=10,  # 10 segundos máximo
                env=env
            )
            
            if process.returncode == 0:
                print(f"   ✅ ¡ÉXITO! pg_dump funcionó con host '{host}'")
                print(f"   📊 Tamaño de salida: {len(process.stdout)} bytes")
                return host  # Retorna el host que funciona
            else:
                print(f"   ❌ Falló con código: {process.returncode}")
                if process.stderr:
                    error_msg = process.stderr.decode()[:200]  # Primeros 200 caracteres
                    print(f"   🔴 Error: {error_msg}")
                    
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout - comando tomó más de 10 segundos")
        except FileNotFoundError:
            print(f"   ❌ pg_dump no encontrado en PATH")
            break  # No tiene sentido seguir probando
        except Exception as e:
            print(f"   ❌ Error inesperado: {e}")
    
    return None

def test_psql_connection():
    """Probar conexión básica con psql"""
    
    print(f"\n🔍 PROBANDO CONEXIÓN BÁSICA CON PSQL")
    print("=" * 40)
    
    db_settings = settings.DATABASES['default']
    
    # Probar comando simple con psql
    for host in ["127.0.0.1", "localhost"]:
        print(f"\n🔗 Probando conexión psql con host '{host}'")
        
        command = [
            'psql',
            '--host', host,
            '--port', str(db_settings['PORT']),
            '--username', db_settings['USER'],
            '--dbname', db_settings['NAME'],
            '--command', 'SELECT version();'
        ]
        
        env = {'PGPASSWORD': db_settings['PASSWORD']}
        
        try:
            process = subprocess.run(
                command,
                capture_output=True,
                timeout=5,
                env=env
            )
            
            if process.returncode == 0:
                print(f"   ✅ Conexión exitosa con psql")
                version = process.stdout.decode().strip()
                print(f"   📊 Versión: {version[:100]}...")
                return host
            else:
                print(f"   ❌ Falló: {process.stderr.decode()[:100]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None

def suggest_fix(working_host):
    """Sugerir la corrección basada en el host que funciona"""
    
    print(f"\n💡 SUGERENCIA DE CORRECCIÓN")
    print("=" * 30)
    
    if working_host:
        print(f"✅ Host que funciona: '{working_host}'")
        print(f"\n🔧 Para arreglar el sistema de backups:")
        print(f"   1. Cambiar en el código de views.py:")
        print(f"      De: '--host', db_settings['HOST']")
        print(f"      A:  '--host', '{working_host}'")
        print(f"\n   2. O mejor aún, cambiar la configuración de la base de datos")
        print(f"      para usar '{working_host}' en lugar de 'localhost'")
    else:
        print(f"❌ Ningún host funcionó")
        print(f"\n🔧 Posibles soluciones:")
        print(f"   1. Verificar que PostgreSQL esté ejecutándose")
        print(f"   2. Verificar que el puerto 5432 esté abierto")
        print(f"   3. Verificar configuración de pg_hba.conf")
        print(f"   4. Probar reiniciar servicio PostgreSQL")

if __name__ == "__main__":
    working_host = test_different_hosts()
    working_psql_host = test_psql_connection()
    suggest_fix(working_host or working_psql_host)