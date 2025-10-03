# apps/tenants/management/commands/verify_tenants.py

from django.core.management.base import BaseCommand
from django.db import connection
from apps.tenants.models import Clinic, Domain


class Command(BaseCommand):
    help = 'Verifica que los inquilinos fueron creados correctamente'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Verificación de Inquilinos ===\n'))
        
        # Verificar clínicas creadas
        clinics = Clinic.objects.all()
        self.stdout.write(f'🏥 Total de clínicas: {clinics.count()}')
        
        for clinic in clinics:
            self.stdout.write(f'   • {clinic.name} (esquema: {clinic.schema_name})')
        
        # Verificar dominios
        domains = Domain.objects.all()
        self.stdout.write(f'\n🌐 Total de dominios: {domains.count()}')
        
        for domain in domains:
            primary = "✅ Principal" if domain.is_primary else "❌ Secundario"
            self.stdout.write(f'   • {domain.domain} → {domain.tenant.name} ({primary})')
        
        # Verificar esquemas en la base de datos
        self.stdout.write('\n📊 Esquemas en PostgreSQL:')
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                ORDER BY schema_name;
            """)
            schemas = cursor.fetchall()
            
            for schema in schemas:
                schema_name = schema[0]
                self.stdout.write(f'   • {schema_name}')
                
                # Contar tablas en cada esquema
                cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = '{schema_name}';
                """)
                table_count = cursor.fetchone()[0]
                self.stdout.write(f'     └─ {table_count} tablas')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Verificación de inquilinos completada!'))