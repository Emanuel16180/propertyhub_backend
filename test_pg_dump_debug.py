#!/usr/bin/env python
"""
Script para probar directamente el comando pg_dump y diagnosticar el problema
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

def test_pg_dump_command():
    """Probar el comando pg_dump exactamente como lo hace la vista"""
    
    print("🔧 DIAGNÓSTICO DEL COMANDO PG_DUMP")
    print("=" * 45)
    
    # Usar la misma configuración que la vista
    db_settings = settings.DATABASES['default']
    schema_name = "bienestar"  # Usar como ejemplo
    
    print(f"📊 Configuración:")
    print(f"   - Base de datos: {db_settings['NAME']}")
    print(f"   - Host: {db_settings['HOST']}")
    print(f"   - Puerto: {db_settings['PORT']}")
    print(f"   - Usuario: {db_settings['USER']}")
    print(f"   - Schema: {schema_name}")
    
    # Construir el comando exacto
    command = [
        'pg_dump',
        '--dbname', db_settings['NAME'],
        '--host', db_settings['HOST'],
        '--port', str(db_settings['PORT']),
        '--username', db_settings['USER'],
        '--schema', schema_name,
        '--format', 'p',
        '--inserts',
        '--no-owner',
        '--no-privileges'
    ]
    
    env = {'PGPASSWORD': db_settings['PASSWORD']}
    
    print(f"\n🔍 Comando que se ejecuta:")
    print(f"   {' '.join(command)}")
    
    print(f"\n🔄 Intentando ejecutar...")
    
    try:
        # Intentar el comando exactamente como en la vista
        process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            env=env
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            print(f"✅ ¡pg_dump ejecutado exitosamente!")
            print(f"📊 Tamaño de salida: {len(stdout)} bytes")
            print(f"📄 Primeras líneas del backup:")
            print("   " + "\n   ".join(stdout.decode()[:500].split('\n')[:5]))
        else:
            print(f"❌ pg_dump falló con código: {process.returncode}")
            print(f"🔴 Error stderr: {stderr.decode()}")
            
    except FileNotFoundError as e:
        print(f"❌ ERROR: pg_dump no encontrado")
        print(f"🔴 Detalle: {e}")
        print(f"💡 Solución: Añadir PostgreSQL bin al PATH del sistema")
        
        # Buscar posibles ubicaciones de pg_dump
        possible_paths = [
            "C:\\Program Files\\PostgreSQL\\17\\bin\\pg_dump.exe",
            "C:\\Program Files\\PostgreSQL\\16\\bin\\pg_dump.exe",
            "C:\\Program Files\\PostgreSQL\\15\\bin\\pg_dump.exe",
            "C:\\PostgreSQL\\bin\\pg_dump.exe"
        ]
        
        print(f"\n🔍 Buscando pg_dump en ubicaciones comunes:")
        for path in possible_paths:
            if os.path.exists(path):
                print(f"   ✅ Encontrado: {path}")
            else:
                print(f"   ❌ No existe: {path}")
                
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")
        print(f"🔴 Tipo de error: {type(e).__name__}")

def check_environment():
    """Verificar variables de entorno y PATH"""
    
    print(f"\n🌍 VERIFICACIÓN DE ENTORNO")
    print("=" * 30)
    
    # Verificar PATH
    path_env = os.environ.get('PATH', '')
    postgres_paths = [p for p in path_env.split(';') if 'postgres' in p.lower()]
    
    if postgres_paths:
        print(f"✅ PostgreSQL encontrado en PATH:")
        for path in postgres_paths:
            print(f"   - {path}")
    else:
        print(f"❌ PostgreSQL NO encontrado en PATH")
    
    # Verificar variables específicas de PostgreSQL
    pg_vars = ['PGHOST', 'PGPORT', 'PGUSER', 'PGPASSWORD', 'PGDATABASE']
    print(f"\n📋 Variables de PostgreSQL:")
    for var in pg_vars:
        value = os.environ.get(var, 'No definida')
        print(f"   {var}: {value}")

if __name__ == "__main__":
    test_pg_dump_command()
    check_environment()
    
    print(f"\n📝 PRÓXIMOS PASOS:")
    print(f"   1. Si pg_dump no se encuentra, añadir al PATH:")
    print(f"      C:\\Program Files\\PostgreSQL\\17\\bin")
    print(f"   2. Reiniciar VS Code y terminal")
    print(f"   3. Probar crear backup desde el frontend")
    print(f"   4. Revisar terminal Django para el mensaje detallado")