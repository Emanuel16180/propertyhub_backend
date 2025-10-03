# apps/tenants/auth_backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django_tenants.utils import get_public_schema_name, get_tenant_model
from django.db import connection
from .models import PublicUser

class TenantAwareAuthBackend(ModelBackend):
    """
    Backend de autenticación que usa diferentes modelos según el esquema
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')
        
        if username is None or password is None:
            return None
        
        # Determinar qué modelo usar según el esquema actual
        if connection.schema_name == get_public_schema_name():
            # Estamos en el esquema público, usar PublicUser
            User = PublicUser
        else:
            # Estamos en un esquema de tenant, usar CustomUser
            User = get_user_model()
        
        try:
            user = User.objects.get(email=username)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            # Ejecutar hasher para evitar ataques de timing
            User().set_password(password)
            return None
    
    def get_user(self, user_id):
        # Determinar qué modelo usar según el esquema actual
        if connection.schema_name == get_public_schema_name():
            User = PublicUser
        else:
            User = get_user_model()
        
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None