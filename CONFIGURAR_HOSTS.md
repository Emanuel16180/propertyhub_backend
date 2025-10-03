# Instrucciones para configurar el archivo hosts

Para que funcione bienestar.localhost, necesitas añadir esta línea al archivo hosts:

## Opción 1: Manual (Recomendado)
1. Abre el Bloc de notas como ADMINISTRADOR
2. Abre el archivo: C:\Windows\System32\drivers\etc\hosts
3. Añade esta línea al final:
   127.0.0.1  bienestar.localhost
4. Guarda el archivo

## Opción 2: PowerShell como Administrador
Ejecuta PowerShell como administrador y ejecuta:
Add-Content -Path "C:\Windows\System32\drivers\etc\hosts" -Value "127.0.0.1  bienestar.localhost"

## Verificación
Después de añadir la línea, puedes verificar que funciona con:
ping bienestar.localhost

Deberías ver respuestas desde 127.0.0.1