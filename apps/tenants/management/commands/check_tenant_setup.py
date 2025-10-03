# apps/tenants/management/commands/check_tenant_setup.py

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Verifica la configuración multi-inquilino'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Verificación de Configuración Multi-Inquilino ===\n'))
        
        # Verificar configuración de apps
        self.stdout.write(f'✅ SHARED_APPS ({len(settings.SHARED_APPS)} apps):')
        for app in settings.SHARED_APPS:
            self.stdout.write(f'   • {app}')
        
        self.stdout.write(f'\n✅ TENANT_APPS ({len(settings.TENANT_APPS)} apps):')
        for app in settings.TENANT_APPS:
            self.stdout.write(f'   • {app}')
        
        self.stdout.write(f'\n✅ INSTALLED_APPS total: {len(settings.INSTALLED_APPS)} apps')
        
        # Verificar configuración de tenant
        self.stdout.write(f'\n✅ TENANT_MODEL: {settings.TENANT_MODEL}')
        self.stdout.write(f'✅ TENANT_DOMAIN_MODEL: {settings.TENANT_DOMAIN_MODEL}')
        
        # Verificar middleware
        tenant_middleware = 'django_tenants.middleware.main.TenantMainMiddleware'
        if tenant_middleware in settings.MIDDLEWARE:
            middleware_index = settings.MIDDLEWARE.index(tenant_middleware)
            if middleware_index == 0:
                self.stdout.write('✅ TenantMainMiddleware está correctamente en primera posición')
            else:
                self.stdout.write(self.style.WARNING(f'⚠️  TenantMainMiddleware está en posición {middleware_index + 1}, debería estar en posición 1'))
        else:
            self.stdout.write(self.style.ERROR('❌ TenantMainMiddleware no encontrado en MIDDLEWARE'))
        
        # Verificar base de datos
        db_engine = settings.DATABASES['default']['ENGINE']
        if 'postgresql' in db_engine:
            self.stdout.write('✅ Base de datos PostgreSQL configurada correctamente')
        else:
            self.stdout.write(self.style.ERROR(f'❌ Base de datos debe ser PostgreSQL, actual: {db_engine}'))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Configuración básica completada. Lista para el siguiente paso!'))