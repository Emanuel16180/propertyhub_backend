# apps/tenants/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_tenants.utils import tenant_context
from .models import Clinic, Domain
from .serializers import ClinicSerializer, ClinicCreateSerializer

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