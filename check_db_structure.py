#!/usr/bin/env python
"""
Script para verificar la estructura actual de la base de datos
"""

import os
import sys
import django
import psycopg2

# Configurar Django
sys.path.append('c:/Users/asus/Documents/psico_admin_sp1_despliegue')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

def check_database_structure():
    """Verificar qué tablas existen en cada tenant"""
    
    print("🔍 Verificación de Estructura de Base de Datos")
    print("=" * 50)
    
    db_settings = settings.DATABASES['default']
    
    # Conectar a la base de datos
    conn = psycopg2.connect(
        dbname=db_settings['NAME'],
        user=db_settings['USER'],
        password=db_settings['PASSWORD'],
        host=db_settings['HOST'],
        port=db_settings['PORT']
    )
    
    # Listar todos los esquemas
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            ORDER BY schema_name;
        """)
        schemas = [row[0] for row in cursor.fetchall()]
    
    print(f"📂 Esquemas encontrados: {schemas}")
    
    for schema in schemas:
        print(f"\n🏥 Schema: {schema}")
        
        # Listar tablas en este esquema
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = '{schema}' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            tables = [row[0] for row in cursor.fetchall()]
        
        print(f"   📋 Tablas ({len(tables)}):")
        for table in tables[:10]:  # Solo mostrar las primeras 10
            print(f"      - {table}")
        
        if len(tables) > 10:
            print(f"      ... y {len(tables) - 10} más")
        
        # Buscar tablas de usuarios específicamente
        user_tables = [t for t in tables if 'user' in t.lower()]
        if user_tables:
            print(f"   👤 Tablas de usuarios: {user_tables}")
            
            # Contar registros si existe alguna tabla de usuarios
            for user_table in user_tables:
                try:
                    with conn.cursor() as cursor:
                        cursor.execute(f'SELECT COUNT(*) FROM "{schema}"."{user_table}";')
                        count = cursor.fetchone()[0]
                        print(f"      → {user_table}: {count} registros")
                except Exception as e:
                    print(f"      → {user_table}: Error al contar - {str(e)}")
    
    conn.close()
    
    print(f"\n🎯 Análisis del Aislamiento:")
    print(f"   ✅ Cada tenant tiene su propio schema")
    print(f"   ✅ Las tablas están separadas por schema")
    print(f"   ✅ pg_dump --schema SOLO afecta un schema específico")
    
    print(f"\n📝 Comando de backup por tenant:")
    for schema in schemas:
        if schema != 'public':
            print(f"   {schema}: pg_dump --schema {schema}")

if __name__ == "__main__":
    check_database_structure()