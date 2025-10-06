# apps/tenants/views.py

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_tenants.utils import tenant_context, schema_context
from .models import Clinic, Domain
from .serializers import ClinicSerializer, ClinicCreateSerializer
import logging

logger = logging.getLogger(__name__)

class ClinicListCreateView(generics.ListCreateAPIView):
    """
    Vista para listar y crear clínicas.
    Solo disponible en el esquema público.
    """
    queryset = Clinic.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ClinicCreateSerializer
        return ClinicSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            clinic = serializer.save()
            # Devolver la respuesta con el serializer de lectura
            response_serializer = ClinicSerializer(clinic)
            return Response(
                response_serializer.data, 
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': f'Error creando la clínica: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class ClinicDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para obtener, actualizar y eliminar una clínica específica.
    """
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    permission_classes = [IsAuthenticated]
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Verificar que no sea la clínica pública
        if instance.schema_name == 'public':
            return Response(
                {'error': 'No se puede eliminar el esquema público'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Eliminar dominios asociados
        Domain.objects.filter(tenant=instance).delete()
        
        # Eliminar la clínica (esto también eliminará el esquema)
        self.perform_destroy(instance)
        
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def global_admin_stats(request):
    """
    Endpoint para obtener estadísticas globales de todas las clínicas.
    Solo accesible desde el schema público por administradores globales.
    """
    # Verificar que estamos en el schema público
    try:
        current_schema = request.tenant.schema_name
        if current_schema != 'public':
            return Response(
                {'error': 'Este endpoint solo está disponible desde el admin global'}, 
                status=status.HTTP_403_FORBIDDEN
            )
    except AttributeError:
        return Response(
            {'error': 'No se pudo determinar el schema actual'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verificar que el usuario es un superuser o staff del schema público
    if not (request.user.is_superuser or request.user.is_staff):
        return Response(
            {'error': 'Permisos insuficientes para acceder a estadísticas globales'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Obtener todas las clínicas REALES (excluyendo el schema público)
        all_clinics = Clinic.objects.exclude(schema_name='public')
        total_clinics = all_clinics.count()
        
        # Obtener todos los dominios (incluyendo public para conteo total)
        total_domains = Domain.objects.count()
        active_domains = Domain.objects.filter(tenant__isnull=False).count()
        
        # Inicializar contadores globales SOLO para clínicas reales
        total_users_global = 0
        clinic_stats = []
        
        # Procesar cada clínica REAL para obtener estadísticas de usuarios
        for clinic in all_clinics:
            try:
                with schema_context(clinic.schema_name):
                    # Importar CustomUser dentro del contexto del schema
                    from apps.users.models import CustomUser
                    
                    # Contar usuarios en este tenant
                    total_users = CustomUser.objects.count()
                    patients = CustomUser.objects.filter(user_type='patient').count()
                    professionals = CustomUser.objects.filter(user_type='professional').count()
                    admins = CustomUser.objects.filter(user_type='admin').count()
                    
                # Fuera del contexto del schema, obtener dominios
                clinic_domains = Domain.objects.filter(tenant=clinic)
                domains_list = [domain.domain for domain in clinic_domains]
                primary_domain = clinic_domains.filter(is_primary=True).first()
                
                clinic_data = {
                    'id': clinic.id,
                    'name': clinic.name,
                    'schema_name': clinic.schema_name,
                    'created_on': clinic.created_on,
                    'total_users': total_users,
                    'patients': patients,
                    'professionals': professionals,
                    'admins': admins,
                    'domains': domains_list,
                    'primary_domain': primary_domain.domain if primary_domain else None,
                    'admin_url': f"http://{primary_domain.domain}:8000/admin/" if primary_domain else None,
                    'frontend_url': f"http://{primary_domain.domain}:3000" if primary_domain else None
                }
                
                clinic_stats.append(clinic_data)
                total_users_global += total_users
                
                logger.info(f"Estadísticas obtenidas para {clinic.name}: {total_users} usuarios")
                
            except Exception as e:
                logger.error(f"Error obteniendo estadísticas para {clinic.name}: {str(e)}")
                # Agregar clínica con datos de error
                clinic_stats.append({
                    'id': clinic.id,
                    'name': clinic.name,
                    'schema_name': clinic.schema_name,
                    'created_on': clinic.created_on,
                    'total_users': 0,
                    'patients': 0,
                    'professionals': 0,
                    'admins': 0,
                    'domains': [],
                    'primary_domain': None,
                    'admin_url': None,
                    'frontend_url': None,
                    'error': f"Error: {str(e)}"
                })
        
        # Preparar respuesta con estadísticas globales
        response_data = {
            'system_status': 'active',
            'total_clinics': total_clinics,
            'total_domains': total_domains,
            'active_domains': active_domains,
            'total_users_global': total_users_global,
            'clinics': clinic_stats,
            'last_updated': request.tenant.created_on if hasattr(request.tenant, 'created_on') else None
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error en global_admin_stats: {str(e)}")
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def clinic_detail_stats(request, clinic_id):
    """
    Obtener estadísticas detalladas de una clínica específica.
    """
    try:
        clinic = Clinic.objects.get(id=clinic_id)
        
        with schema_context(clinic.schema_name):
            # Importar modelos dentro del contexto
            from apps.users.models import CustomUser
            
            # Estadísticas básicas
            total_users = CustomUser.objects.count()
            patients = CustomUser.objects.filter(user_type='patient').count()
            professionals = CustomUser.objects.filter(user_type='professional').count()
            admins = CustomUser.objects.filter(user_type='admin').count()
            
            # Estadísticas avanzadas (opcional)
            try:
                from apps.appointments.models import Appointment
                from apps.professionals.models import ProfessionalProfile
                
                total_appointments = Appointment.objects.count()
                pending_appointments = Appointment.objects.filter(status='pending').count()
                confirmed_appointments = Appointment.objects.filter(status='confirmed').count()
                
                total_professionals_profiles = ProfessionalProfile.objects.count()
                verified_professionals = ProfessionalProfile.objects.filter(is_verified=True).count()
                
            except ImportError:
                total_appointments = 0
                pending_appointments = 0
                confirmed_appointments = 0
                total_professionals_profiles = 0
                verified_professionals = 0
            
            response_data = {
                'clinic': {
                    'id': clinic.id,
                    'name': clinic.name,
                    'schema_name': clinic.schema_name,
                    'created_on': clinic.created_on
                },
                'users': {
                    'total': total_users,
                    'patients': patients,
                    'professionals': professionals,
                    'admins': admins
                },
                'appointments': {
                    'total': total_appointments,
                    'pending': pending_appointments,
                    'confirmed': confirmed_appointments
                },
                'professionals': {
                    'total_profiles': total_professionals_profiles,
                    'verified': verified_professionals
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
    except Clinic.DoesNotExist:
        return Response(
            {'error': 'Clínica no encontrada'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error en clinic_detail_stats: {str(e)}")
        return Response(
            {'error': f'Error interno: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )