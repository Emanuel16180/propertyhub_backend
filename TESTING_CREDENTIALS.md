# 🔑 Credenciales y URLs de Prueba - Sistema Multi-Tenant

## 🌐 URLs de Acceso

### Backend (Django)
```
🌐 Admin Global:     http://localhost:8000/admin/
🏥 Admin Bienestar:  http://bienestar.localhost:8000/admin/
🧠 Admin MindCare:   http://mindcare.localhost:8000/admin/

📡 APIs Bienestar:   http://bienestar.localhost:8000/api/
📡 APIs MindCare:    http://mindcare.localhost:8000/api/

🔍 Debug Endpoints:
   - http://localhost:8000/debug/
   - http://bienestar.localhost:8000/debug/
   - http://mindcare.localhost:8000/debug/
```

### Frontend (React)
```
🌐 App Global:       http://localhost:3000        → Admin de clínicas
🏥 App Bienestar:    http://bienestar.localhost:3000 → Portal de Bienestar
🧠 App MindCare:     http://mindcare.localhost:3000  → Portal de MindCare
```

## 🔑 Credenciales de Acceso

### 🌐 Admin Global (localhost:8000/admin/)
```
Email:    admin@psico.com
Password: admin123
Acceso:   Gestión de clínicas y dominios
```

### 🏥 Clínica Bienestar (bienestar.localhost:8000/admin/)
```
Usuario 1:
Email:    admin@gmail.com
Password: password123
Acceso:   Admin completo de la clínica

Usuario 2:
Email:    madmin@gmail.com  
Password: password123
Acceso:   Admin completo de la clínica
```

### 🧠 Clínica MindCare (mindcare.localhost:8000/admin/)
```
Email:    admin@gmail.com
Password: password123
Acceso:   Admin completo de la clínica
```

## 📊 Datos de Prueba Disponibles

### Clínica Bienestar
- **Usuarios:** 121 usuarios registrados
- **Profesionales:** Psicólogos con especialidades
- **Citas:** Citas de prueba con diferentes estados
- **Chat:** Mensajes entre pacientes y profesionales

### Clínica MindCare  
- **Usuarios:** 60 usuarios registrados
- **Profesionales:** Psicólogos con especialidades
- **Citas:** Citas de prueba con diferentes estados
- **Chat:** Mensajes entre pacientes y profesionales

## 🧪 Tests de Funcionalidad

### ✅ Verificaciones Básicas

1. **Resolución de Tenants:**
   ```bash
   curl http://localhost:8000/debug/
   # Debería mostrar: "schema_name": "public"
   
   curl http://bienestar.localhost:8000/debug/
   # Debería mostrar: "schema_name": "bienestar"
   
   curl http://mindcare.localhost:8000/debug/
   # Debería mostrar: "schema_name": "mindcare"
   ```

2. **APIs por Tenant:**
   ```bash
   # Público - 404 (correcto)
   curl http://localhost:8000/api/professionals/
   
   # Bienestar - 200 con datos
   curl http://bienestar.localhost:8000/api/professionals/
   
   # MindCare - 200 con datos
   curl http://mindcare.localhost:8000/api/professionals/
   ```

3. **Admin Sites Diferenciados:**
   - localhost:8000/admin/ → Solo "GESTIÓN DE CLÍNICAS"
   - bienestar.localhost:8000/admin/ → Sin "GESTIÓN DE CLÍNICAS"
   - mindcare.localhost:8000/admin/ → Sin "GESTIÓN DE CLÍNICAS"

### 🔐 Tests de Autenticación

#### API Login - Bienestar
```bash
curl -X POST http://bienestar.localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@gmail.com",
    "password": "password123"
  }'
```

#### API Login - MindCare
```bash
curl -X POST http://mindcare.localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@gmail.com", 
    "password": "password123"
  }'
```

### 📱 Tests Frontend

#### Comandos de Desarrollo
```bash
# Terminal 1 - Backend
python manage.py runserver

# Terminal 2 - Frontend Bienestar
npm run start:bienestar

# Terminal 3 - Frontend MindCare  
npm run start:mindcare

# Terminal 4 - Frontend Global
npm run start:global
```

#### Flujo de Prueba
1. **Configurar hosts:**
   ```
   127.0.0.1    bienestar.localhost
   127.0.0.1    mindcare.localhost
   ```

2. **Probar Login en cada tenant:**
   - Bienestar: http://bienestar.localhost:3000/login
   - MindCare: http://mindcare.localhost:3000/login
   - Global: http://localhost:3000/login

3. **Verificar datos aislados:**
   - Cada clínica debe ver solo SUS usuarios
   - Cada clínica debe ver solo SUS citas
   - Admin global debe ver solo gestión de clínicas

## 🚀 Comandos de Gestión

### Crear Nueva Clínica
```python
# python manage.py shell
from apps.tenants.models import Clinic, Domain

# Crear clínica
nueva_clinica = Clinic.objects.create(
    name="Clínica Nueva",
    schema_name="nueva"
)

# Crear dominio
Domain.objects.create(
    domain="nueva.localhost",
    tenant=nueva_clinica,
    is_primary=True
)

print(f"✅ Clínica creada: {nueva_clinica.name}")
```

### Poblar Datos de Prueba
```bash
# Crear especializaciones
python manage.py create_specializations

# Poblar con datos fake
python manage.py populate_db

# Crear disponibilidades
python manage.py create_availability
```

### Crear Usuarios Admin
```python
# Para tenant específico
from django_tenants.utils import schema_context
from apps.tenants.models import Clinic
from apps.users.models import CustomUser

clinic = Clinic.objects.get(schema_name='nueva')
with schema_context(clinic.schema_name):
    admin = CustomUser.objects.create_superuser(
        email='admin@nueva.com',
        password='admin123',
        first_name='Admin',
        last_name='Nueva'
    )
```

## 📋 Checklist de Verificación

### Backend ✅
- [ ] Django server corriendo en puerto 8000
- [ ] Todos los dominios resuelven correctamente
- [ ] APIs funcionan solo en tenants apropiados
- [ ] Admin sites muestran contenido diferenciado
- [ ] Autenticación funciona por tenant

### Frontend ✅  
- [ ] Variables de entorno configuradas por tenant
- [ ] ApiClient configurado con dominios correctos
- [ ] AuthService maneja storage por tenant
- [ ] Componentes se adaptan según tenant
- [ ] Navegación funciona correctamente

### Producción 🚀
- [ ] CORS configurado para dominios de producción
- [ ] Variables de entorno de producción configuradas
- [ ] SSL configurado para todos los dominios
- [ ] Base de datos de producción configurada
- [ ] Redis configurado para sessions/cache
- [ ] Archivos estáticos servidos correctamente

## 🛠️ Troubleshooting

### Problema: "URLs no se resuelven"
```bash
# Verificar que django-tenants está funcionando
python manage.py shell -c "
from django_tenants.utils import get_tenant_model
print('Tenants:', list(get_tenant_model().objects.all()))
"
```

### Problema: "APIs dan 404 en tenants"
```bash
# Verificar URLconf
curl -v http://bienestar.localhost:8000/debug/
# Debe mostrar que usa config.urls, no config.urls_public
```

### Problema: "Admin muestra modelos incorrectos"
- Verificar que admin sites están separados
- Confirmar que modelos están registrados en el admin correcto
- Reiniciar servidor después de cambios en admin

¡Con esta información tienes todo lo necesario para probar y desarrollar con el sistema multi-tenant! 🎉