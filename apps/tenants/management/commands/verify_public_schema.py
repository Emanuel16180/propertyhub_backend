# apps/tenants/management/commands/verify_public_schema.py

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Verifica que el esquema público fue creado correctamente'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Verificación del Esquema Público ===\n'))
        
        with connection.cursor() as cursor:
            # Verificar que estamos en el esquema público
            cursor.execute("SELECT current_schema();")
            current_schema = cursor.fetchone()[0]
            self.stdout.write(f'📍 Esquema actual: {current_schema}')
            
            # Buscar las tablas de tenants específicamente
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'tenants_%'
                ORDER BY table_name;
            """)
            tenant_tables = cursor.fetchall()
            
            if tenant_tables:
                self.stdout.write('\n✅ Tablas de tenants encontradas:')
                for table in tenant_tables:
                    self.stdout.write(f'   • {table[0]}')
            else:
                self.stdout.write(self.style.ERROR('\n❌ No se encontraron tablas de tenants'))
            
            # Verificar todas las tablas del esquema público
            cursor.execute("""
                SELECT COUNT(*) as total_tables
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """)
            total_tables = cursor.fetchone()[0]
            self.stdout.write(f'\n📊 Total de tablas en esquema público: {total_tables}')
            
            # Verificar que podemos consultar la tabla de clínicas
            try:
                cursor.execute("SELECT COUNT(*) FROM tenants_clinic;")
                clinic_count = cursor.fetchone()[0]
                self.stdout.write(f'🏥 Clínicas registradas: {clinic_count}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error consultando tenants_clinic: {e}'))
            
            # Verificar que podemos consultar la tabla de dominios
            try:
                cursor.execute("SELECT COUNT(*) FROM tenants_domain;")
                domain_count = cursor.fetchone()[0]
                self.stdout.write(f'🌐 Dominios registrados: {domain_count}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error consultando tenants_domain: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Verificación del esquema público completada!'))