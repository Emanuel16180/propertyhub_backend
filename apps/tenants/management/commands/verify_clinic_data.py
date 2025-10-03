# apps/tenants/management/commands/verify_clinic_data.py

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Verifica los datos en el esquema de una clínica específica'

    def add_arguments(self, parser):
        parser.add_argument('--schema', type=str, default='bienestar', help='Esquema de la clínica a verificar')

    def handle(self, *args, **options):
        schema = options['schema']
        self.stdout.write(self.style.SUCCESS(f'=== Verificación de Datos - Clínica ({schema}) ===\n'))
        
        # Importar modelos después de configurar el esquema
        from apps.users.models import CustomUser
        from apps.professionals.models import ProfessionalProfile, Specialization
        from apps.appointments.models import Appointment, PsychologistAvailability
        
        # Verificar usuarios
        total_users = CustomUser.objects.count()
        patients = CustomUser.objects.filter(user_type='patient').count()
        professionals = CustomUser.objects.filter(user_type='professional').count()
        
        self.stdout.write(f'👥 Total usuarios: {total_users}')
        self.stdout.write(f'   • Pacientes: {patients}')
        self.stdout.write(f'   • Profesionales: {professionals}')
        
        # Verificar profesionales
        professional_profiles = ProfessionalProfile.objects.count()
        self.stdout.write(f'\n👨‍⚕️ Perfiles profesionales: {professional_profiles}')
        
        # Verificar especializaciones
        specializations = Specialization.objects.count()
        self.stdout.write(f'🎓 Especializaciones: {specializations}')
        
        # Verificar citas
        appointments = Appointment.objects.count()
        pending_appointments = Appointment.objects.filter(status='pending').count()
        confirmed_appointments = Appointment.objects.filter(status='confirmed').count()
        completed_appointments = Appointment.objects.filter(status='completed').count()
        
        self.stdout.write(f'\n📅 Total citas: {appointments}')
        self.stdout.write(f'   • Pendientes: {pending_appointments}')
        self.stdout.write(f'   • Confirmadas: {confirmed_appointments}')
        self.stdout.write(f'   • Completadas: {completed_appointments}')
        
        # Verificar disponibilidad
        availability_slots = PsychologistAvailability.objects.count()
        self.stdout.write(f'⏰ Slots de disponibilidad: {availability_slots}')
        
        # Mostrar algunos ejemplos
        if patients > 0:
            sample_patient = CustomUser.objects.filter(user_type='patient').first()
            self.stdout.write(f'\n👤 Paciente de ejemplo: {sample_patient.get_full_name()} ({sample_patient.email})')
        
        if professionals > 0:
            sample_professional = CustomUser.objects.filter(user_type='professional').first()
            self.stdout.write(f'👨‍⚕️ Profesional de ejemplo: {sample_professional.get_full_name()} ({sample_professional.email})')
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 Verificación de la clínica "{schema}" completada!'))