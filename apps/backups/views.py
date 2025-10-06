# apps/backups/views.py

import subprocess
import datetime
import psycopg2
import json
import os
import tempfile
from django.conf import settings
from django.http import HttpResponse
from django.core.management import call_command
from io import StringIO
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from apps.clinic_admin.permissions import IsClinicAdmin
import logging

logger = logging.getLogger(__name__)

class CreateBackupAndDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClinicAdmin]

    def post(self, request, *args, **kwargs):
        # Primero, intenta crear el respaldo con pg_dump
        try:
            logger.info("Intentando crear backup con pg_dump...")
            return self._create_backup_with_pg_dump(request)
        except Exception as e:
            logger.warning(f"pg_dump falló con el error: {e}. Usando el método de respaldo de Django.")
            # Si pg_dump falla por cualquier razón, usa el método de Django
            return self._create_backup_with_django(request)

    def _create_backup_with_pg_dump(self, request):
        """Genera un backup en formato .sql usando la herramienta pg_dump."""
        schema_name = request.tenant.schema_name
        db_settings = settings.DATABASES['default']
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
        filename = f"backup-sql-{schema_name}-{timestamp}.sql"

        command = [
            'pg_dump', '--dbname', db_settings['NAME'], '--host', db_settings['HOST'],
            '--port', str(db_settings['PORT']), '--username', db_settings['USER'],
            '--schema', schema_name, '--format', 'p', '--inserts', '--no-owner', '--no-privileges'
        ]
        env = {'PGPASSWORD': db_settings['PASSWORD']}

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            # Si hay un error, lo lanza para que sea capturado por el try...except principal
            raise subprocess.CalledProcessError(process.returncode, command, stderr=stderr)

        response = HttpResponse(stdout, content_type='application/sql')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def _create_backup_with_django(self, request):
        """Método de fallback que usa 'dumpdata' de Django para crear un backup .json."""
        schema_name = request.tenant.schema_name
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
        filename = f"backup-json-{schema_name}-{timestamp}.json"

        buffer = StringIO()
        # Especificamos las apps que pertenecen a un tenant para no incluir las compartidas innecesarias
        tenant_apps = ['users', 'professionals', 'appointments', 'chat', 'clinical_history', 'payment_system']
        call_command('dumpdata', *tenant_apps, format='json', indent=2, stdout=buffer)
        buffer.seek(0)

        response = HttpResponse(buffer.getvalue(), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class RestoreBackupFromFileView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClinicAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        if 'backup_file' not in request.FILES:
            return Response({'error': 'No se proporcionó ningún archivo.'}, status=status.HTTP_400_BAD_REQUEST)

        backup_file = request.FILES['backup_file']

        if backup_file.name.endswith('.sql'):
            return self._restore_sql_backup(request, backup_file)
        elif backup_file.name.endswith('.json'):
            return self._restore_json_backup(request, backup_file)
        else:
            return Response({'error': 'Formato de archivo no soportado. Use .sql o .json.'}, status=status.HTTP_400_BAD_REQUEST)

    def _restore_sql_backup(self, request, backup_file):
        schema_name = request.tenant.schema_name
        db_settings = settings.DATABASES['default']
        env = {'PGPASSWORD': db_settings['PASSWORD']}
        try:
            conn = psycopg2.connect(
                dbname=db_settings['NAME'], user=db_settings['USER'],
                password=db_settings['PASSWORD'], host=db_settings['HOST'], port=db_settings['PORT']
            )
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE;')
                cursor.execute(f'CREATE SCHEMA "{schema_name}";')
                cursor.execute(f'GRANT ALL ON SCHEMA "{schema_name}" TO "{db_settings["USER"]}";')
            conn.close()

            restore_command = [
                'psql', '--dbname', db_settings['NAME'], '--host', db_settings['HOST'],
                '--port', str(db_settings['PORT']), '--username', db_settings['USER'],
                '--single-transaction'
            ]
            process = subprocess.run(restore_command, input=backup_file.read(), capture_output=True, check=True, env=env)
            return Response({'status': 'Restauración desde SQL completada.'}, status=status.HTTP_200_OK)
        except subprocess.CalledProcessError as e:
            return Response({'error': f"Error en la restauración SQL: {e.stderr.decode()}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _restore_json_backup(self, request, backup_file):
        """Restaura desde un archivo JSON usando archivos temporales."""
        temp_file_path = None
        try:
            # 1. Crear un archivo temporal seguro
            with tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.json', encoding='utf-8') as temp_file:
                # Escribir el contenido del archivo subido al archivo temporal
                temp_file.write(backup_file.read().decode('utf-8'))
                temp_file_path = temp_file.name
            
            # 2. Borrar solo los datos del tenant actual usando ORM (más seguro)
            self._clear_tenant_data_safe()
            
            # 3. Cargar los datos desde el archivo temporal
            call_command('loaddata', temp_file_path)
            
            return Response({'status': 'Restauración desde JSON completada.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error en restauración JSON: {str(e)}")
            return Response({'error': f"Error en la restauración JSON: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            # 4. Asegurarse de que el archivo temporal se borre siempre
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logger.info(f"Archivo temporal eliminado: {temp_file_path}")
                except Exception as e:
                    logger.warning(f"No se pudo eliminar archivo temporal {temp_file_path}: {e}")

    def _clear_tenant_data_safe(self):
        """Borra solo los datos del tenant actual usando ORM de Django (método más seguro)."""
        try:
            # Importar modelos localmente para evitar problemas de importación circular
            from apps.users.models import CustomUser, PatientProfile, ProfessionalProfile
            from apps.appointments.models import Appointment, PsychologistAvailability
            from apps.chat.models import ChatMessage
            
            # Borrar en orden para respetar foreign keys
            logger.info("Iniciando limpieza de datos del tenant...")
            
            # 1. Borrar mensajes de chat
            ChatMessage.objects.all().delete()
            logger.info("Mensajes de chat eliminados")
            
            # 2. Borrar citas
            Appointment.objects.all().delete()
            logger.info("Citas eliminadas")
            
            # 3. Borrar disponibilidades
            PsychologistAvailability.objects.all().delete()
            logger.info("Disponibilidades eliminadas")
            
            # 4. Borrar perfiles de pacientes y profesionales
            PatientProfile.objects.all().delete()
            ProfessionalProfile.objects.all().delete()
            logger.info("Perfiles eliminados")
            
            # 5. Borrar usuarios (excepto superusuarios para evitar problemas)
            CustomUser.objects.filter(is_superuser=False).delete()
            logger.info("Usuarios no-admin eliminados")
            
            logger.info("Limpieza de datos del tenant completada exitosamente")
            
        except Exception as e:
            logger.error(f"Error en limpieza segura de datos: {e}")
            # Si falla todo, intentar un método alternativo más agresivo
            try:
                from django.db import connection
                schema_name = connection.tenant.schema_name
                logger.warning(f"Intentando limpieza alternativa para {schema_name}")
                
                with connection.cursor() as cursor:
                    # Borrar solo las tablas principales del tenant
                    tables_to_clear = [
                        'chat_chatmessage',
                        'appointments_appointment', 
                        'appointments_psychologistavailability',
                        'users_patientprofile',
                        'users_professionalprofile',
                    ]
                    
                    for table in tables_to_clear:
                        try:
                            cursor.execute(f'DELETE FROM "{table}"')
                            logger.info(f"Tabla {table} limpiada")
                        except Exception as table_error:
                            logger.warning(f"No se pudo limpiar {table}: {table_error}")
                            
            except Exception as fallback_error:
                logger.error(f"Error en método de limpieza alternativo: {fallback_error}")
                raise