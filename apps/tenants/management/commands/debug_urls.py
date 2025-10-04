from django.core.management.base import BaseCommand
from django.db import connection
from django.urls import get_resolver
from django.conf import settings

class Command(BaseCommand):
    help = 'Debug tenant URL resolution'

    def handle(self, *args, **options):
        print(f"Current schema: {connection.schema_name}")
        
        resolver = get_resolver()
        print(f"Current URLconf: {resolver.urlconf_name}")
        print(f"ROOT_URLCONF setting: {getattr(settings, 'ROOT_URLCONF', 'NOT SET')}")
        print(f"TENANT_URLCONF setting: {getattr(settings, 'TENANT_URLCONF', 'NOT SET')}")
        
        print("\nAvailable URL patterns:")
        for i, pattern in enumerate(resolver.url_patterns[:10]):
            print(f"  {i+1}. {pattern.pattern}")