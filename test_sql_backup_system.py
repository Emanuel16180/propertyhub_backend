#!/usr/bin/env python
"""
Script para probar el sistema de backup robusto con archivos .sql
"""

import os
import sys
import django
import psycopg2
from datetime import datetime

# Configurar Django
sys.path.append('c:/Users/asus/Documents/psico_admin_sp1_despliegue')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

def test_sql_backup_system():
    """Probar el nuevo sistema de backup SQL robusto"""
    
    print("🔧 Prueba del Sistema de Backup Robusto SQL")
    print("=" * 50)
    
    # Configuración de base de datos
    db_settings = settings.DATABASES['default']
    
    print(f"📊 Configuración:")
    print(f"   - Base de datos: {db_settings['NAME']}")
    print(f"   - Host: {db_settings['HOST']}:{db_settings['PORT']}")
    print(f"   - Usuario: {db_settings['USER']}")
    
    # Probar conexión a PostgreSQL
    try:
        conn = psycopg2.connect(
            dbname=db_settings['NAME'],
            user=db_settings['USER'],
            password=db_settings['PASSWORD'],
            host=db_settings['HOST'],
            port=db_settings['PORT']
        )
        print(f"✅ Conexión a PostgreSQL exitosa")
        
        # Listar esquemas disponibles
        with conn.cursor() as cursor:
            cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast');")
            schemas = [row[0] for row in cursor.fetchall()]
            
        print(f"📂 Esquemas disponibles: {schemas}")
        
        # Verificar disponibilidad de herramientas PostgreSQL
        import subprocess
        
        try:
            result = subprocess.run(['pg_dump', '--version'], capture_output=True, text=True, check=True)
            print(f"✅ pg_dump disponible: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ pg_dump no disponible")
            
        try:
            result = subprocess.run(['psql', '--version'], capture_output=True, text=True, check=True)
            print(f"✅ psql disponible: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ psql no disponible")
        
        # Comprobar contenido de un esquema específico
        for schema in ['bienestar', 'mindcare']:
            if schema in schemas:
                with conn.cursor() as cursor:
                    cursor.execute(f"""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = '{schema}' 
                        AND table_type = 'BASE TABLE'
                        ORDER BY table_name;
                    """)
                    tables = [row[0] for row in cursor.fetchall()]
                    
                print(f"📋 Tablas en esquema '{schema}': {len(tables)} tablas")
                
                # Contar registros en tablas importantes
                important_tables = ['users_customuser', 'users_patientprofile', 'professionals_professionalprofile']
                for table in important_tables:
                    if table in tables:
                        with conn.cursor() as cursor:
                            cursor.execute(f'SELECT COUNT(*) FROM "{schema}"."{table}";')
                            count = cursor.fetchone()[0]
                            print(f"   - {table}: {count} registros")
        
        conn.close()
        
        print(f"\n🎯 Nuevo Sistema de Backup:")
        print(f"   - Formato: SQL de texto plano (.sql)")
        print(f"   - Creación: pg_dump --format=p --inserts")
        print(f"   - Restauración: psql --single-transaction")
        print(f"   - Limpieza: DROP CASCADE + CREATE SCHEMA")
        print(f"   - Validación: check=True para errores confiables")
        
        print(f"\n✅ Sistema listo para pruebas con archivos .sql")
        print(f"📝 Próximo paso: Crear backup -> Eliminar datos -> Restaurar -> Verificar")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_sql_backup_system()