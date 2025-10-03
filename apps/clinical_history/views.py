# apps/clinical_history/views.py

from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from django.db.models import Q
from .models import SessionNote, ClinicalDocument
from .serializers import SessionNoteSerializer, ClinicalDocumentSerializer, PsychologistPatientSerializer
from apps.appointments.models import Appointment
from apps.users.models import CustomUser

class IsAssociatedProfessional(permissions.BasePermission):
    """
    Permiso personalizado para asegurar que solo el psicólogo de la cita
    pueda acceder a la nota.
    """
    def has_permission(self, request, view):
        # Solo los usuarios tipo 'professional' pueden acceder.
        if request.user.user_type != 'professional':
            return False
        
        # Obtenemos el ID de la cita desde la URL.
        appointment_id = view.kwargs.get('appointment_pk')
        try:
            appointment = Appointment.objects.get(pk=appointment_id)
            # Verificamos si el usuario actual es el psicólogo de esa cita.
            return request.user == appointment.psychologist
        except Appointment.DoesNotExist:
            return False

class SessionNoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para crear y gestionar notas de sesión.
    Accesible a través de /api/appointments/appointments/<appointment_pk>/note/
    """
    serializer_class = SessionNoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsAssociatedProfessional]

    def get_queryset(self):
        # Este ViewSet solo se usa para una cita específica, no para listar todas.
        appointment_id = self.kwargs.get('appointment_pk')
        return SessionNote.objects.filter(appointment_id=appointment_id)

    def perform_create(self, serializer):
        # Asignamos la cita automáticamente desde la URL.
        appointment_id = self.kwargs.get('appointment_pk')
        appointment = Appointment.objects.get(pk=appointment_id)
        serializer.save(appointment=appointment)

    def create(self, request, *args, **kwargs):
        # Prevenimos que se cree más de una nota por cita.
        appointment_id = self.kwargs.get('appointment_pk')
        if SessionNote.objects.filter(appointment_id=appointment_id).exists():
            return Response(
                {"error": "Ya existe una nota para esta cita."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Obtener la nota de la cita específica (debería ser máximo 1)
        """
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset.first())
            return Response(serializer.data)
        else:
            return Response(
                {"message": "No hay nota para esta cita"},
                status=status.HTTP_404_NOT_FOUND
            )


# --- NUEVAS VISTAS PARA DOCUMENTOS CLÍNICOS ---

class MyDocumentsListView(generics.ListAPIView):
    """
    Endpoint para que un paciente vea todos los documentos que le han subido.
    (CU-39 - Vista del Paciente)
    """
    serializer_class = ClinicalDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Solo mostrar si el usuario es paciente
        if self.request.user.user_type != 'patient':
            return ClinicalDocument.objects.none()
        
        # Devuelve solo los documentos del usuario autenticado
        return ClinicalDocument.objects.filter(patient=self.request.user)


class MyPastPatientsListView(generics.ListAPIView):
    """
    Endpoint para que un psicólogo obtenga una lista de todos los pacientes
    con los que ha tenido una cita.
    (CU-39 - Vista del Psicólogo para seleccionar paciente)
    """
    serializer_class = PsychologistPatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Solo mostrar si el usuario es psicólogo
        if self.request.user.user_type != 'professional':
            return CustomUser.objects.none()
            
        psychologist = self.request.user
        # Obtiene los IDs de todos los pacientes que han tenido una cita con el psicólogo
        patient_ids = Appointment.objects.filter(psychologist=psychologist)\
                                         .values_list('patient_id', flat=True)\
                                         .distinct()
        # Devuelve la lista de esos usuarios
        return CustomUser.objects.filter(id__in=patient_ids)


class DocumentUploadView(generics.CreateAPIView):
    """
    Endpoint para que un psicólogo suba un documento a un paciente específico.
    (CU-39 - Acción de Subir)
    """
    serializer_class = ClinicalDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Asigna al psicólogo actual como la persona que sube el archivo
        serializer.save(uploaded_by=self.request.user)

    def create(self, request, *args, **kwargs):
        # Solo psicólogos pueden subir documentos
        if request.user.user_type != 'professional':
            return Response(
                {"error": "Solo los psicólogos pueden subir documentos."},
                status=status.HTTP_403_FORBIDDEN
            )

        # --- Validación de Permiso Clave ---
        # Verifica si el psicólogo tiene permiso para subir archivos a este paciente
        patient_id = request.data.get('patient')
        if not patient_id:
            return Response(
                {"error": "Debe especificar un paciente."},
                status=status.HTTP_400_BAD_REQUEST
            )

        psychologist = request.user

        has_had_appointment = Appointment.objects.filter(
            psychologist=psychologist,
            patient_id=patient_id
        ).exists()

        if not has_had_appointment:
            return Response(
                {"error": "No tienes permiso para subir documentos a este paciente. Solo puedes subir documentos a pacientes con los que has tenido una cita."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().create(request, *args, **kwargs)
