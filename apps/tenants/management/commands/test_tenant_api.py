# apps/tenants/management/commands/test_tenant_api.py

from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth import get_user_model
import json

User = get_user_model()


class Command(BaseCommand):
    help = 'Prueba el acceso a la API por tenant'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Prueba de API Multi-Tenant ===\n'))
        
        # Crear cliente de prueba
        client = Client()
        
        # Probar acceso al tenant público
        self.stdout.write('🔍 Probando acceso al tenant público (localhost)...')
        response = client.get('/api/professionals/', HTTP_HOST='localhost')
        self.stdout.write(f'   Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            self.stdout.write(f'   Profesionales encontrados: {len(data)}')
        
        # Probar acceso al tenant de bienestar
        self.stdout.write('\n🔍 Probando acceso al tenant bienestar (bienestar.localhost)...')
        response = client.get('/api/professionals/', HTTP_HOST='bienestar.localhost')
        self.stdout.write(f'   Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            self.stdout.write(f'   Profesionales encontrados: {len(data)}')
            
            if len(data) > 0:
                sample_prof = data[0]
                self.stdout.write(f'   Ejemplo: {sample_prof.get("full_name", "N/A")}')
        
        # Probar endpoint de especialidades
        self.stdout.write('\n🔍 Probando especialidades en bienestar...')
        response = client.get('/api/professionals/specializations/', HTTP_HOST='bienestar.localhost')
        self.stdout.write(f'   Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            self.stdout.write(f'   Especializaciones: {len(data)}')
        
        # Información sobre autenticación
        self.stdout.write('\n📋 Para probar autenticación:')
        
        # Buscar un paciente de ejemplo
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO bienestar;")
                sample_patient = User.objects.filter(user_type='patient').first()
                if sample_patient:
                    self.stdout.write(f'   📧 Email de paciente ejemplo: {sample_patient.email}')
                    self.stdout.write('   🔑 Contraseña: password123')
                
                sample_professional = User.objects.filter(user_type='professional').first()
                if sample_professional:
                    self.stdout.write(f'   👨‍⚕️ Email de profesional ejemplo: {sample_professional.email}')
                    self.stdout.write('   🔑 Contraseña: password123')
        except Exception as e:
            self.stdout.write(f'   ⚠️  Error obteniendo usuarios de ejemplo: {e}')
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 Prueba de API multi-tenant completada!'))