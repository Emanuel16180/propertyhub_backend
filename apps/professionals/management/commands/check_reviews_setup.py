# apps/professionals/management/commands/check_reviews_setup.py

from django.core.management.base import BaseCommand
from apps.appointments.models import Appointment
from apps.professionals.models import Review
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Verifica el estado del sistema de reseñas'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Estado del Sistema de Reseñas ===\n'))
        
        # Verificar citas
        total_appointments = Appointment.objects.count()
        completed_appointments = Appointment.objects.filter(status='completed').count()
        
        self.stdout.write(f'📅 Total de citas: {total_appointments}')
        self.stdout.write(f'✅ Citas completadas: {completed_appointments}')
        
        # Verificar usuarios
        patients = User.objects.filter(user_type='patient').count()
        professionals = User.objects.filter(user_type='professional').count()
        
        self.stdout.write(f'👤 Pacientes: {patients}')
        self.stdout.write(f'👨‍⚕️ Profesionales: {professionals}')
        
        # Verificar reseñas
        total_reviews = Review.objects.count()
        self.stdout.write(f'⭐ Total de reseñas: {total_reviews}')
        
        # Mostrar algunas citas completadas
        if completed_appointments > 0:
            self.stdout.write('\n📋 Citas completadas disponibles para reseña:')
            for appointment in Appointment.objects.filter(status='completed')[:5]:
                has_review = hasattr(appointment, 'review')
                review_status = '✅ Ya tiene reseña' if has_review else '❌ Sin reseña'
                self.stdout.write(
                    f'  • ID {appointment.id}: {appointment.patient.get_full_name()} → '
                    f'{appointment.psychologist.get_full_name()} ({review_status})'
                )
        else:
            self.stdout.write(self.style.WARNING('\n⚠️  No hay citas completadas para reseñar'))
            
        # Mostrar reseñas existentes
        if total_reviews > 0:
            self.stdout.write('\n⭐ Reseñas existentes:')
            for review in Review.objects.all()[:5]:
                self.stdout.write(
                    f'  • {review.patient.get_full_name()} → '
                    f'{review.professional.user.get_full_name()}: {review.rating}/5 estrellas'
                )