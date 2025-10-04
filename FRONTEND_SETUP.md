# 🚀 CONFIG### 🏢 **Administrador General** (Esquema Público)
- **URL**: `http://localhost:8000`
- **Admin Web**: `http://localhost:8000/admin/` ✅
- **Credenciales**: `admin@psico.com` / `admin`
- **Función**: Gestiona clínicas y configuración global del sistema
- **Autenticación**: Solo via interfaz web de Django Admin (no API)
- **Uso**: Acceso directo al admin panel, no requiere tokensN FRONTEND - SISTEMA MULTI-TENANT

## ✅ ESTADO ACTUAL
- **Backend corriendo**: `http://127.0.0.1:8000`
- **CORS configurado**: ✅ Funcional para todos los orígenes
- **Autenticación**: ✅ Funcionando en ambos tenants
- **Multi-tenant**: ✅ URLs separadas por dominio
- **Backend Auth Fix**: ✅ TenantAwareAuthBackend funcionando correctamente

## 🌐 DOMINIOS DISPONIBLES

### � **Administrador General** (Esquema Público)
- **URL**: `http://localhost:8000`
- **Admin**: `http://localhost:8000/admin/`
- **API Base**: `http://localhost:8000/api/`
- **Credenciales**: `admin@psico.com` / `admin`
- **Función**: Gestiona clínicas y configuración global del sistema

### �🏥 Tenant: Bienestar
- **URL**: `http://bienestar.localhost:8000`
- **Admin**: `http://bienestar.localhost:8000/admin/`
- **API Base**: `http://bienestar.localhost:8000/api/`
- **Credenciales**: `admin@gmail.com` / `admin`

### 🏥 Tenant: Mindcare  
- **URL**: `http://mindcare.localhost:8000`
- **Admin**: `http://mindcare.localhost:8000/admin/`
- **API Base**: `http://mindcare.localhost:8000/api/`
- **Credenciales**: `admin@gmail.com` / `admin`

## 🎯 ENDPOINTS PRINCIPALES

```javascript
// Autenticación
POST /api/auth/login/
POST /api/auth/register/
POST /api/auth/logout/

// Ejemplo de uso desde React:
const response = await fetch('http://bienestar.localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Origin': 'http://localhost:5174' // Tu puerto de desarrollo
  },
  body: JSON.stringify({
    email: 'admin@gmail.com',
    password: 'admin'
  })
});
```

## � ARQUITECTURA DE AUTENTICACIÓN

### 🏢 **Administrador Global (localhost:8000)**
- **Tipo**: Autenticación por sesiones Django
- **Modelo**: `PublicUser` 
- **Acceso**: Solo via Django Admin web interface
- **Credenciales**: `admin@psico.com` / `admin`
- **URL**: `http://localhost:8000/admin/`

### 🏥 **Clínicas (subdominios)**
- **Tipo**: Autenticación por tokens REST API
- **Modelo**: `CustomUser`
- **Acceso**: API endpoints con tokens JWT/DRF
- **Credenciales**: `admin@gmail.com` / `admin`
- **URLs API**: 
  - `http://bienestar.localhost:8000/api/auth/login/`
  - `http://mindcare.localhost:8000/api/auth/login/`

### ⚠️ **Separación Importante**
- **localhost:8000**: NO tiene endpoints `/api/auth/` (solo admin web)
- **subdominios**: SÍ tienen endpoints `/api/auth/` (para frontend)

## 🔒 CONFIGURACIÓN CORS

### ✅ Orígenes Permitidos
- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite) 
- `http://localhost:5174` (Vite alternativo)
- `http://localhost:8080` (Vue/webpack)
- `http://localhost:4200` (Angular)
- `http://bienestar.localhost:5174`
- `http://mindcare.localhost:5174`
- `http://bienestar.localhost:3000`
- `http://mindcare.localhost:3000`

### 📋 Headers Permitidos
- `authorization` (para tokens)
- `content-type`
- `origin`
- `accept`
- `x-requested-with`
- `cache-control`
- `x-api-key`

### 🔄 Métodos Permitidos
- `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`

## 🎮 CONFIGURACIÓN DEL FRONTEND

### Para React/Vite:
```javascript
// .env.local
VITE_API_BASE_URL_PUBLIC=http://localhost:8000
VITE_API_BASE_URL_BIENESTAR=http://bienestar.localhost:8000
VITE_API_BASE_URL_MINDCARE=http://mindcare.localhost:8000

// utils/api.js
const getApiBaseUrl = (tenant) => {
  switch(tenant) {
    case 'public': return import.meta.env.VITE_API_BASE_URL_PUBLIC;
    case 'bienestar': return import.meta.env.VITE_API_BASE_URL_BIENESTAR;
    case 'mindcare': return import.meta.env.VITE_API_BASE_URL_MINDCARE;
    default: return import.meta.env.VITE_API_BASE_URL_PUBLIC;
  }
};

export const apiCall = async (tenant, endpoint, options = {}) => {
  const baseUrl = getApiBaseUrl(tenant);
  const response = await fetch(`${baseUrl}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  });
  return response.json();
};
```

### Para Next.js:
```javascript
// next.config.js
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/bienestar/:path*',
        destination: 'http://bienestar.localhost:8000/api/:path*'
      },
      {
        source: '/api/mindcare/:path*', 
        destination: 'http://mindcare.localhost:8000/api/:path*'
      }
    ];
  }
};
```

## 🧪 PRUEBAS DE CONECTIVIDAD

### Desde JavaScript (navegador):
```javascript
// Verificar conexión a Bienestar
fetch('http://bienestar.localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'admin@gmail.com', password: 'admin' })
})
.then(r => r.json())
.then(data => console.log('Bienestar:', data));

// Verificar conexión a Mindcare
fetch('http://mindcare.localhost:8000/api/auth/login/', {
  method: 'POST', 
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'admin@gmail.com', password: 'admin' })
})
.then(r => r.json())
.then(data => console.log('Mindcare:', data));
```

## ⚡ NOTAS IMPORTANTES

1. **Hosts file**: Asegúrate de tener en `C:\Windows\System32\drivers\etc\hosts`:
   ```
   127.0.0.1 bienestar.localhost
   127.0.0.1 mindcare.localhost
   ```

2. **Puerto del servidor**: El backend debe estar corriendo en el puerto 8000
   ```bash
   python manage.py runserver
   ```

3. **Desarrollo local**: Los subdominios `*.localhost` funcionan automáticamente en navegadores modernos

4. **Autenticación**: Cada tenant tiene sus propios usuarios aislados

5. **HTTPS**: Para desarrollo local no es necesario, pero en producción sí

## 🔧 TROUBLESHOOTING

### Si no funciona el login:
1. Verificar que el servidor esté corriendo
2. Verificar el host correcto (`bienestar.localhost` vs `mindcare.localhost`)
3. Verificar credenciales por tenant
4. Revisar la consola del navegador para errores CORS

### Si CORS falla:
1. Verificar que el `Origin` header coincida con los permitidos
2. Verificar que el método HTTP esté permitido
3. Verificar headers enviados

¡Todo listo para conectar el frontend! 🎉