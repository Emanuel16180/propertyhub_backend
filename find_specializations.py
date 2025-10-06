#!/usr/bin/env python
"""
Verificar tablas específicas en la base de datos
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

def find_specializations_table():
    """Buscar la tabla specializations en todos los esquemas"""
    
    print("🔍 Búsqueda de la tabla 'specializations'")
    print("=" * 45)
    
    db_settings = settings.DATABASES['default']
    
    # Conectar a la base de datos
    conn = psycopg2.connect(
        dbname=db_settings['NAME'],
        user=db_settings['USER'],
        password=db_settings['PASSWORD'],
        host=db_settings['HOST'],
        port=db_settings['PORT']
    )
    
    schemas = ['public', 'bienestar', 'mindcare']
    
    for schema in schemas:
        print(f"\n🏥 Schema: {schema}")
        
        # Buscar tabla specializations
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = '{schema}' 
                AND table_name = 'specializations';
            """)
            result = cursor.fetchall()
            
            if result:
                print(f"   ✅ Tabla 'specializations' encontrada")
                
                # Contar registros
                try:
                    cursor.execute(f'SELECT COUNT(*) FROM "{schema}".specializations;')
                    count = cursor.fetchone()[0]
                    print(f"   📊 Registros: {count}")
                except Exception as e:
                    print(f"   ❌ Error al contar: {e}")
            else:
                print(f"   ❌ Tabla 'specializations' NO encontrada")
                
                # Buscar tablas relacionadas con professionals
                cursor.execute(f"""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = '{schema}' 
                    AND table_name LIKE '%profession%'
                    ORDER BY table_name;
                """)
                prof_tables = [row[0] for row in cursor.fetchall()]
                
                if prof_tables:
                    print(f"   📋 Tablas de professionals: {prof_tables}")
                else:
                    print(f"   📋 No hay tablas de professionals")
    
    conn.close()
    
    print(f"\n🎯 Conclusión:")
    print(f"   Si no existe 'specializations', necesitamos:")
    print(f"   1. Verificar las migraciones")
    print(f"   2. Forzar recreación de la tabla")
    print(f"   3. O usar un modelo diferente")

if __name__ == "__main__":
    find_specializations_table()