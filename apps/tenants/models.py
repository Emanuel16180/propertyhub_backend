# apps/tenants/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django_tenants.models import TenantMixin, DomainMixin

class PublicUserManager(BaseUserManager):
    """Manager para usuarios del esquema público"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class PublicUser(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuario simple para el esquema público.
    Solo para gestionar clínicas, no para datos clínicos.
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    # Evitar conflictos con CustomUser usando related_name
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='public_users',
        related_query_name='public_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='public_users',
        related_query_name='public_user',
    )

    objects = PublicUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @property
    def username(self):
        """Retorna el email como username para compatibilidad con admin"""
        return self.email

    def get_full_name(self):
        """Retorna el nombre completo del usuario"""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Retorna el primer nombre"""
        return self.first_name

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Usuario Público'
        verbose_name_plural = 'Usuarios Públicos'

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

class Clinic(TenantMixin):
    """
    Este es el modelo que representa a cada inquilino (cada clínica).
    """
    name = models.CharField(max_length=100)
    created_on = models.DateField(auto_now_add=True)

    # auto_create_schema se asegura de que django-tenants cree automáticamente
    # un nuevo esquema en la base de datos cuando se crea una nueva clínica.
    auto_create_schema = True

    def __str__(self):
        return self.name

class Domain(DomainMixin):
    """
    Este modelo representa los dominios o subdominios asociados a cada clínica.
    """
    pass