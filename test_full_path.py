#!/usr/bin/env python
"""
Probar pg_dump con ruta completa
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

def test_full_path():
    """Probar con ruta completa"""
    
    print("🔧 PROBANDO CON RUTA COMPLETA")
    print("=" * 35)
    
    db_settings = settings.DATABASES['default']
    schema_name = "bienestar"
    
    # Usar exactamente el mismo comando que ahora está en views.py
    pg_dump_path = r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe"
    command = [
        pg_dump_path,
        '--dbname', db_settings['NAME'],
        '--host', '127.0.0.1',  # IP en lugar de localhost
        '--port', str(db_settings['PORT']),
        '--username', db_settings['USER'],
        '--schema', schema_name,
        '--format', 'p',
        '--inserts',
        '--no-owner',
        '--no-privileges'
    ]
    
    env = {'PGPASSWORD': db_settings['PASSWORD']}
    
    print(f"📍 Comando: {' '.join(command)}")
    print(f"🔄 Ejecutando...")
    
    try:
        process = subprocess.run(
            command,
            capture_output=True,
            timeout=15,
            env=env
        )
        
        if process.returncode == 0:
            print(f"✅ ¡ÉXITO! pg_dump funcionó")
            print(f"📊 Tamaño de backup: {len(process.stdout)} bytes")
            print(f"📄 Primeras líneas:")
            lines = process.stdout.decode()[:500].split('\n')[:5]
            for line in lines:
                print(f"   {line}")
        else:
            print(f"❌ Falló con código: {process.returncode}")
            print(f"🔴 stderr: {process.stderr.decode()}")
            print(f"🔴 stdout: {process.stdout.decode()}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_full_path()