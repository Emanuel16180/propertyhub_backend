from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from apps.users.models import CustomUser
from apps.users.serializers import UserDetailSerializer
from apps.professionals.models import ProfessionalProfile
from .permissions import IsClinicAdmin


class UserManagementViewSet(viewsets.ModelViewSet):
    """
    Gestión de usuarios (pacientes y profesionales) para administradores de la clínica.
    CU-30: Administrar usuarios.
    Incluye acción para verificar profesionales (CU-07).
    """
    serializer_class = UserDetailSerializer
    permission_classes = [IsClinicAdmin]

    def get_queryset(self):
        qs = CustomUser.objects.all().order_by('-date_joined')
        # Filtros opcionales (búsqueda rápida por email/nombre o tipo)
        user_type = self.request.query_params.get('user_type')
        search = self.request.query_params.get('search')
        if user_type:
            qs = qs.filter(user_type=user_type)
        if search:
            qs = qs.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        return qs

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active'])

    @action(detail=True, methods=['post'], url_path='verify-profile')
    def verify_profile(self, request, pk=None):
        user = self.get_object()
        if user.user_type != 'professional':
            return Response({'error': 'Este usuario no es un profesional.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            profile = user.professional_profile
        except ProfessionalProfile.DoesNotExist:
            return Response({'error': 'Este profesional no tiene un perfil para verificar.'}, status=status.HTTP_404_NOT_FOUND)
        if getattr(profile, 'is_verified', None) is True:
            return Response({'status': 'El perfil ya estaba verificado.'}, status=status.HTTP_200_OK)
        setattr(profile, 'is_verified', True)
        profile.save(update_fields=['is_verified'])
        return Response({'status': 'Perfil profesional verificado con éxito.'})
