# config/admin_site.py

from django.contrib import admin
from apps.tenants.models import Clinic, Domain, PublicUser
from apps.tenants.forms import PublicAdminAuthenticationForm

class PublicAdminSite(admin.AdminSite):
    """
    Admin site personalizado para el esquema público.
    Solo gestiona clínicas y dominios, sin logs ni funcionalidades complejas.
    """
    site_header = "Administración Global de Psico SAS"
    site_title = "Admin Global"
    index_title = "Gestión de Clínicas"
    
    # Le decimos que use nuestro formulario de login personalizado
    login_form = PublicAdminAuthenticationForm

class TenantAdminSite(admin.AdminSite):
    """
    Admin site específico para tenants individuales (clínicas).
    Muestra todas las funcionalidades normales de Django admin
    para gestionar usuarios, citas, chats, etc.
    SIN mostrar gestión de clínicas.
    """
    site_header = "Administración de Clínica"
    site_title = "Admin Clínica" 
    index_title = "Panel de Control"
    
    def each_context(self, request):
        """
        Personalizar el contexto para mostrar información del tenant actual
        """
        context = super().each_context(request)
        
        # Intentar obtener información del tenant actual
        if hasattr(request, 'tenant'):
            context['tenant_name'] = getattr(request.tenant, 'name', 'Clínica')
            context['site_header'] = f"Administración de {context['tenant_name']}"
        
        return context

# Instancias de los admin sites
public_admin_site = PublicAdminSite(name='public_admin')
tenant_admin_site = TenantAdminSite(name='tenant_admin')

# --- ADMIN CLASSES PARA PÚBLICO ---

class ClinicAdmin(admin.ModelAdmin):
    """Admin para gestionar clínicas"""
    list_display = ('name', 'schema_name', 'created_on')
    search_fields = ('name', 'schema_name')
    readonly_fields = ('created_on',)
    list_filter = ('created_on',)

class DomainAdmin(admin.ModelAdmin):
    """Admin para gestionar dominios"""
    list_display = ('domain', 'tenant', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('domain',)

class PublicUserAdmin(admin.ModelAdmin):
    """Admin simplificado para usuarios públicos"""
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    ordering = ('email',)
    
    fields = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')

# --- REGISTRAR MODELOS SOLO EN ADMIN PÚBLICO ---
public_admin_site.register(Clinic, ClinicAdmin)
public_admin_site.register(Domain, DomainAdmin)
public_admin_site.register(PublicUser, PublicUserAdmin)

# --- REGISTRAR MODELOS SOLO EN ADMIN DE TENANTS ---
# Importar modelos y admins de tenants
from apps.users.models import CustomUser, PatientProfile
from apps.users.admin import CustomUserAdmin, PatientProfileAdmin

from apps.professionals.models import ProfessionalProfile, Specialization, WorkingHours, Review
from apps.professionals.admin import ProfessionalProfileAdmin, SpecializationAdmin, ReviewAdmin

from apps.appointments.models import Appointment, PsychologistAvailability
from apps.appointments.admin import AppointmentAdmin, PsychologistAvailabilityAdmin

from apps.chat.models import ChatMessage
from apps.chat.admin import ChatMessageAdmin

# Registrar SOLO en el admin de tenants
tenant_admin_site.register(CustomUser, CustomUserAdmin)
tenant_admin_site.register(PatientProfile, PatientProfileAdmin)
tenant_admin_site.register(ProfessionalProfile, ProfessionalProfileAdmin)
tenant_admin_site.register(Specialization, SpecializationAdmin)
tenant_admin_site.register(WorkingHours)
tenant_admin_site.register(Review, ReviewAdmin)
tenant_admin_site.register(Appointment, AppointmentAdmin)
tenant_admin_site.register(PsychologistAvailability, PsychologistAvailabilityAdmin)
tenant_admin_site.register(ChatMessage, ChatMessageAdmin)