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

# --- REGISTRAR MODELOS EN ADMIN DE TENANTS ---
# Importar y registrar todos los modelos de las apps de tenants

# 1. Usuarios y Perfiles
try:
    from apps.users.models import CustomUser, PatientProfile
    from apps.users.admin import CustomUserAdmin, PatientProfileAdmin
    tenant_admin_site.register(CustomUser, CustomUserAdmin)
    tenant_admin_site.register(PatientProfile, PatientProfileAdmin)
except ImportError:
    pass

# 2. Profesionales
try:
    from apps.professionals.models import ProfessionalProfile, Specialization, WorkingHours, Review
    from apps.professionals.admin import ProfessionalProfileAdmin, SpecializationAdmin, ReviewAdmin
    tenant_admin_site.register(ProfessionalProfile, ProfessionalProfileAdmin)
    tenant_admin_site.register(Specialization, SpecializationAdmin)
    tenant_admin_site.register(WorkingHours)  # Sin admin personalizado
    tenant_admin_site.register(Review, ReviewAdmin)
except ImportError:
    pass

# 3. Citas
try:
    from apps.appointments.models import Appointment, PsychologistAvailability
    from apps.appointments.admin import AppointmentAdmin, PsychologistAvailabilityAdmin
    tenant_admin_site.register(Appointment, AppointmentAdmin)
    tenant_admin_site.register(PsychologistAvailability, PsychologistAvailabilityAdmin)
except ImportError:
    pass

# 4. Chat
try:
    from apps.chat.models import ChatMessage
    from apps.chat.admin import ChatMessageAdmin
    # ChatMessage ya se registra en su propio admin.py, pero lo agregamos aquí también
    if not tenant_admin_site.is_registered(ChatMessage):
        tenant_admin_site.register(ChatMessage, ChatMessageAdmin)
except ImportError:
    pass

# 5. Historia Clínica
try:
    from apps.clinical_history.models import SessionNote, ClinicalDocument
    from apps.clinical_history.admin import SessionNoteAdmin, ClinicalDocumentAdmin
    # Estos modelos ya se registran en su admin.py, pero los agregamos al tenant admin
    if not tenant_admin_site.is_registered(SessionNote):
        tenant_admin_site.register(SessionNote, SessionNoteAdmin)
    if not tenant_admin_site.is_registered(ClinicalDocument):
        tenant_admin_site.register(ClinicalDocument, ClinicalDocumentAdmin)
except ImportError:
    pass