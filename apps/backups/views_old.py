# apps/backups/views.py

import subprocess
import datetime
import os
import json
import psycopg2  # Para conexiones directas a PostgreSQL
from django.conf import settings
from django.http import StreamingHttpResponse, HttpResponse
from django.core.management import call_command
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from io import StringIO

from apps.clinic_admin.permissions import IsClinicAdmin  # Reutilizamos el permiso de admin

class CreateBackupAndDownloadView(APIView):
    """
    Crea una copia de seguridad del schema del tenant actual y la transmite para su descarga.
    """
    permission_classes = [permissions.IsAuthenticated, IsClinicAdmin]

    def post(self, request, *args, **kwargs):
        schema_name = request.tenant.schema_name
        db_settings = settings.DATABASES['default']

        # Formatear la fecha para el nombre del archivo
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
        filename = f"backup-{schema_name}-{timestamp}.sqlc"  # Cambiamos la extensión por convención

        try:
            # Comando pg_dump para exportar solo el schema del tenant
            command = [
                'pg_dump',
                '--dbname', db_settings['NAME'],
                '--host', db_settings['HOST'],
                '--port', str(db_settings['PORT']),
                '--username', db_settings['USER'],
                '--schema', schema_name,
                '--format', 'c',  # Formato comprimido
                '--no-owner',
                '--no-privileges'
            ]

            # Establecer la contraseña de la base de datos a través de una variable de entorno
            env = os.environ.copy()
            env['PGPASSWORD'] = db_settings['PASSWORD']

            # Intentar ejecutar pg_dump
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                # pg_dump exitoso
                response = HttpResponse(stdout, content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            else:
                # pg_dump falló, usar método alternativo
                return self._create_backup_django_way(schema_name, filename)

        except FileNotFoundError:
            # pg_dump no está disponible, usar método alternativo
            return self._create_backup_django_way(schema_name, filename)
        except Exception as e:
            return Response({'error': f'Error creating backup: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _create_backup_django_way(self, schema_name, filename):
        """
        Método alternativo para crear backup usando Django cuando pg_dump no está disponible
        """
        try:
            # Usar dumpdata de Django para crear un backup en formato JSON
            output = StringIO()
            
            # Cambiar al esquema correcto
            with connection.cursor() as cursor:
                cursor.execute(f'SET search_path TO {schema_name}')
            
            # Obtener todas las apps instaladas para este tenant
            from django.apps import apps
            app_labels = []
            for app_config in apps.get_app_configs():
                if app_config.label in settings.TENANT_APPS:
                    app_labels.append(app_config.label)
            
            # Crear el backup usando dumpdata
            call_command('dumpdata', *app_labels, format='json', indent=2, stdout=output)
            backup_data = output.getvalue()
            
            # Crear respuesta con el backup
            timestamp = datetime.datetime.now().isoformat()
            backup_json = {
                'schema_name': schema_name,
                'created_at': timestamp,
                'backup_method': 'django_dumpdata',
                'data': json.loads(backup_data)
            }
            
            backup_content = json.dumps(backup_json, indent=2)
            filename_json = filename.replace('.sqlc', '.json')
            
            response = HttpResponse(backup_content, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{filename_json}"'
            return response

        except Exception as e:
            return Response({'error': f'Error creating Django backup: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RestoreBackupFromFileView(APIView):
    """
    Restaura una copia de seguridad desde un archivo.
    Esta es una operación destructiva que primero borra el schema actual.
    """
    permission_classes = [permissions.IsAuthenticated, IsClinicAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        if 'backup_file' not in request.FILES:
            return Response({'error': 'No se proporcionó ningún archivo.'}, status=status.HTTP_400_BAD_REQUEST)

        backup_file = request.FILES['backup_file']
        schema_name = request.tenant.schema_name
        db_settings = settings.DATABASES['default']

        # Protección: no permitir restaurar el esquema público
        if schema_name == 'public':
            return Response({'error': 'La restauración del esquema público no está permitida.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            # Determinar el tipo de archivo por la extensión
            if backup_file.name.endswith('.json'):
                return self._restore_django_backup(backup_file, schema_name)
            elif backup_file.name.endswith(('.sql', '.sqlc')):
                return self._restore_sql_backup_robust(backup_file, schema_name, db_settings)
            else:
                return Response({'error': 'Formato de archivo no soportado. Use .sql, .sqlc o .json'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f'Error during restore: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _restore_sql_backup_robust(self, backup_file, schema_name, db_settings):
        """
        Restaurar backup SQL usando método robusto: DROP CASCADE + CREATE + pg_restore
        """
        env = os.environ.copy()
        env['PGPASSWORD'] = db_settings['PASSWORD']

        try:
            # 1. Conexión directa a PostgreSQL para borrar y recrear el schema
            conn = psycopg2.connect(
                dbname=db_settings['NAME'],
                user=db_settings['USER'],
                password=db_settings['PASSWORD'],
                host=db_settings['HOST'],
                port=db_settings['PORT']
            )
            conn.autocommit = True
            
            with conn.cursor() as cursor:
                # 2. Borramos el schema existente de forma segura y forzada
                cursor.execute(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE;')
                
                # 3. Creamos el schema de nuevo, vacío
                cursor.execute(f'CREATE SCHEMA "{schema_name}";')
                
                # 4. Asignamos los permisos necesarios
                cursor.execute(f'GRANT ALL ON SCHEMA "{schema_name}" TO "{db_settings["USER"]}";')
            
            conn.close()

            # 5. Comando pg_restore (SIN --clean, porque ya limpiamos manualmente)
            restore_command = [
                'pg_restore',
                '--dbname', db_settings['NAME'],
                '--host', db_settings['HOST'],
                '--port', str(db_settings['PORT']),
                '--username', db_settings['USER'],
                '--schema', schema_name,
                '--no-owner',
                '--no-privileges'
            ]

            # 6. Ejecutamos la restauración sobre el schema ahora vacío
            process = subprocess.run(
                restore_command, 
                input=backup_file.read(), 
                capture_output=True, 
                check=True,
                env=env
            )
            
            return Response({'status': 'Restauración completada exitosamente.'}, status=status.HTTP_200_OK)

        except psycopg2.Error as e:
            return Response({'error': f'Error de base de datos: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except subprocess.CalledProcessError as e:
            return Response({'error': f'Error en la restauración SQL: {e.stderr.decode()}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except FileNotFoundError:
            # pg_restore no está disponible, intentar método alternativo
            return Response({'error': 'pg_restore no está disponible. Use un archivo .json para restauración Django.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': f'Error general en restauración: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _restore_django_backup(self, backup_file, schema_name):
        """
        Restaurar backup JSON usando loaddata de Django
        """
        try:
            # Leer y parsear el archivo JSON
            backup_content = backup_file.read().decode('utf-8')
            backup_data = json.loads(backup_content)

            # Verificar que es un backup válido
            if 'schema_name' not in backup_data or 'data' not in backup_data:
                return Response({'error': 'Formato de backup JSON inválido.'}, status=status.HTTP_400_BAD_REQUEST)

            # Cambiar al esquema correcto
            with connection.cursor() as cursor:
                cursor.execute(f'SET search_path TO {schema_name}')

            # Crear archivo temporal con los datos
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                json.dump(backup_data['data'], temp_file, indent=2)
                temp_filename = temp_file.name

            try:
                # Usar loaddata para restaurar los datos
                call_command('loaddata', temp_filename)
                return Response({'status': 'Restauración Django completada exitosamente.'}, status=status.HTTP_200_OK)

            finally:
                # Limpiar archivo temporal
                os.unlink(temp_filename)

        except json.JSONDecodeError:
            return Response({'error': 'Archivo JSON inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Error en restauración Django: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
