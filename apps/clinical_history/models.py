# apps/clinical_history/models.py

from django.db import models
from django.conf import settings
from apps.appointments.models import Appointment

class SessionNote(models.Model):
    """
    Modelo para las notas privadas de un profesional sobre una cita específica.
    """
    # Usamos OneToOne para asegurar que solo haya UNA nota por cita.
    appointment = models.OneToOneField(
        Appointment, 
        on_delete=models.CASCADE, 
        related_name='session_note'
    )
    
    content = models.TextField(
        help_text="Notas privadas del profesional sobre la sesión."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment__appointment_date']
        verbose_name = 'Nota de Sesión'
        verbose_name_plural = 'Notas de Sesión'
        db_table = 'session_notes'

    def __str__(self):
        return f"Nota para la cita del {self.appointment.appointment_date} con {self.appointment.patient.get_full_name()}"


class ClinicalDocument(models.Model):
    """
    Modelo para documentos subidos por un profesional para un paciente específico.
    """
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clinical_documents',
        limit_choices_to={'user_type': 'patient'}
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # Si el psicólogo se elimina, no borramos el documento
        null=True,
        related_name='uploaded_documents',
        limit_choices_to={'user_type': 'professional'}
    )
    
    # El archivo en sí
    file = models.FileField(upload_to='clinical_documents/%Y/%m/%d/')
    
    description = models.CharField(max_length=255, help_text="Descripción o título del documento.")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Documento Clínico'
        verbose_name_plural = 'Documentos Clínicos'
        db_table = 'clinical_documents'

    def __str__(self):
        return f"Documento '{self.description}' para {self.patient.get_full_name()}"
