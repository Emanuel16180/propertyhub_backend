# apps/backups/views.py

import subprocess
import datetime
import psycopg2
import json
from django.conf import settings
from django.http import StreamingHttpResponse, HttpResponse
from django.core.management import call_command
from django.db import connection
from io import StringIO
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from apps.clinic_admin.permissions import IsClinicAdmin

class CreateBackupAndDownloadView(APIView):
    """
    Crea una copia de seguridad en formato SQL plano (.sql) y la transmite para descarga.
    """
    permission_classes = [permissions.IsAuthenticated, IsClinicAdmin]

    def post(self, request, *args, **kwargs):
        schema_name = request.tenant.schema_name
        db_settings = settings.DATABASES['default']

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
        filename = f"backup-{schema_name}-{timestamp}.sql"

        # Comando pg_dump para generar SQL plano
        # TEMPORAL: Usar ruta completa para resolver problema de PATH
        pg_dump_path = r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe"
        command = [
            pg_dump_path,  # Usar ruta completa en lugar de 'pg_dump'
            '--dbname', db_settings['NAME'],
            '--host', '127.0.0.1',  # Usar IP en lugar de localhost
            '--port', str(db_settings['PORT']),
            '--username', db_settings['USER'],
            '--schema', schema_name,
            '--format', 'p',  # 'p' para plain-text SQL
            '--inserts',      # Usar comandos INSERT en lugar de COPY
            '--no-owner',
            '--no-privileges'
        ]

        env = {'PGPASSWORD': db_settings['PASSWORD']}

        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)

            response = StreamingHttpResponse(process.stdout, content_type='application/sql')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            stderr = process.communicate()[1]
            if process.returncode != 0:
                print(f"pg_dump falló, stderr: {stderr.decode()}")
                # Fallback: usar método Django si pg_dump falla
                return self._create_backup_django_fallback(schema_name, filename)

            return response
        except Exception as e:
            # --- AÑADE ESTA LÍNEA PARA VER EL ERROR EN LA TERMINAL ---
            print(f"ERROR DETALLADO EN CreateBackupAndDownloadView: {e}")
            # Fallback: usar método Django si pg_dump no está disponible
            return self._create_backup_django_fallback(schema_name, filename)


class RestoreBackupFromFileView(APIView):
    """
    Restaura una copia de seguridad desde un archivo .sql subido por el usuario.
    """
    permission_classes = [permissions.IsAuthenticated, IsClinicAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        if 'backup_file' not in request.FILES:
            return Response({'error': 'No se proporcionó ningún archivo.'}, status=status.HTTP_400_BAD_REQUEST)

        backup_file = request.FILES['backup_file']
        schema_name = request.tenant.schema_name
        db_settings = settings.DATABASES['default']

        if schema_name == 'public':
            return Response({'error': 'La restauración del esquema público no está permitida.'}, status=status.HTTP_403_FORBIDDEN)

        # Verificar tipo de archivo
        if backup_file.name.endswith('.json'):
            return self._restore_django_backup(backup_file, schema_name)
        elif backup_file.name.endswith('.sql'):
            return self._restore_sql_backup(backup_file, schema_name, db_settings)
        else:
            return Response({'error': 'Formato no soportado. Use .sql o .json'}, status=status.HTTP_400_BAD_REQUEST)

    def _restore_sql_backup(self, backup_file, schema_name, db_settings):
        """Restaurar backup SQL usando psql"""
        
        env = {'PGPASSWORD': db_settings['PASSWORD']}

        try:
            # 1. Limpiar y recrear el schema
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

            # 2. Usar psql en lugar de pg_restore para archivos .sql
            # TEMPORAL: Usar ruta completa para resolver problema de PATH
            psql_path = r"C:\Program Files\PostgreSQL\17\bin\psql.exe"
            restore_command = [
                psql_path,  # Usar ruta completa en lugar de 'psql'
                '--dbname', db_settings['NAME'],
                '--host', '127.0.0.1',  # Usar IP en lugar de localhost
                '--port', str(db_settings['PORT']),
                '--username', db_settings['USER'],
                '--single-transaction', # Asegura que toda la restauración ocurra o falle junta
            ]

            process = subprocess.run(
                restore_command, 
                input=backup_file.read(), 
                capture_output=True, 
                check=True, # check=True lanzará una excepción si psql falla
                env=env
            )

            return Response({'status': 'Restauración completada exitosamente.'}, status=status.HTTP_200_OK)

        except subprocess.CalledProcessError as e:
            print(f"ERROR DETALLADO EN RestoreBackupFromFileView (CalledProcessError): {e}")
            return Response({'error': f"Error en la restauración SQL: {e.stderr.decode()}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(f"ERROR DETALLADO EN RestoreBackupFromFileView (Exception): {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _restore_django_backup(self, backup_file, schema_name):
        """Restaurar backup JSON usando Django"""
        
        try:
            print(f"🔄 Restaurando backup Django para schema: {schema_name}")
            
            # Leer y parsear archivo JSON
            backup_content = backup_file.read().decode('utf-8')
            backup_data = json.loads(backup_content)
            
            # Verificar estructura del backup
            if 'data' not in backup_data:
                return Response({'error': 'Formato de backup JSON inválido'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Cambiar al esquema correcto
            with connection.cursor() as cursor:
                cursor.execute(f'SET search_path TO "{schema_name}", public')
            
            # Crear archivo temporal
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                json.dump(backup_data['data'], temp_file, indent=2)
                temp_filename = temp_file.name
            
            try:
                # Restaurar usando loaddata
                call_command('loaddata', temp_filename)
                print(f"✅ Backup Django restaurado exitosamente")
                return Response({'status': 'Restauración Django completada exitosamente'}, status=status.HTTP_200_OK)
                
            finally:
                # Limpiar archivo temporal
                if os.path.exists(temp_filename):
                    os.unlink(temp_filename)
                    
        except json.JSONDecodeError:
            return Response({'error': 'Archivo JSON inválido'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"❌ Error en restauración Django: {str(e)}")
            return Response({'error': f'Error en restauración Django: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _create_backup_django_fallback(self, schema_name, filename):
        """Método de fallback usando Django cuando pg_dump no funciona"""
        
        import json
        from django.core.management import call_command
        from django.db import connection
        from io import StringIO
        from django.http import HttpResponse
        
        try:
            print(f"🔄 Usando método de backup Django para schema: {schema_name}")
            
            # Cambiar al esquema correcto
            with connection.cursor() as cursor:
                cursor.execute(f'SET search_path TO "{schema_name}", public')
            
            # Crear backup usando dumpdata
            output = StringIO()
            
            # Apps relevantes para backup
            tenant_apps = [
                'users', 'professionals', 'appointments', 
                'chat', 'clinical_history'
            ]
            
            call_command('dumpdata', *tenant_apps, format='json', indent=2, stdout=output)
            backup_data = output.getvalue()
            
            # Crear backup estructurado
            timestamp = datetime.datetime.now().isoformat()
            backup_json = {
                'schema_name': schema_name,
                'created_at': timestamp,
                'backup_method': 'django_dumpdata_fallback',
                'format': 'json',
                'data': json.loads(backup_data)
            }
            
            backup_content = json.dumps(backup_json, indent=2)
            filename_json = filename.replace('.sql', '.json')
            
            response = HttpResponse(backup_content, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{filename_json}"'
            
            print(f"✅ Backup Django creado exitosamente: {filename_json}")
            return response

        except Exception as e:
            print(f"❌ Error en backup Django: {str(e)}")
            return Response({'error': f'Error en backup Django: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)