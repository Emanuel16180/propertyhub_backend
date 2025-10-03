# 🏥 Guía de Conexión Frontend → Backend Multi-Tenant

## 📋 Resumen del Sistema Multi-Tenant

Tu backend Django ahora maneja **múltiples clínicas independientes** usando dominios diferentes:

```
🌐 localhost:8000           → Admin Global (gestión de clínicas)
🏥 bienestar.localhost:8000  → Clínica Bienestar  
🧠 mindcare.localhost:8000   → Clínica MindCare
```

## 🔧 Configuración del Frontend

### 1. **Configuración de Dominios Locales**

Cada clínica debe acceder desde su propio dominio. Configura tu archivo `hosts`:

**Windows:** `C:\Windows\System32\drivers\etc\hosts`
**Mac/Linux:** `/etc/hosts`

Añade estas líneas:
```
127.0.0.1    bienestar.localhost
127.0.0.1    mindcare.localhost
```

### 2. **Variables de Entorno por Clínica**

Crea archivos `.env` separados para cada clínica:

#### `.env.bienestar`
```env
REACT_APP_API_BASE_URL=http://bienestar.localhost:8000
REACT_APP_CLINIC_NAME=Clinica Bienestar
REACT_APP_CLINIC_DOMAIN=bienestar.localhost
REACT_APP_TENANT_ID=bienestar
```

#### `.env.mindcare`
```env
REACT_APP_API_BASE_URL=http://mindcare.localhost:8000
REACT_APP_CLINIC_NAME=Clinica MindCare
REACT_APP_CLINIC_DOMAIN=mindcare.localhost
REACT_APP_TENANT_ID=mindcare
```

#### `.env.global` (para admin global)
```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_CLINIC_NAME=Administración Global
REACT_APP_CLINIC_DOMAIN=localhost
REACT_APP_TENANT_ID=public
```

### 3. **Scripts de Desarrollo por Clínica**

Modifica tu `package.json`:

```json
{
  "scripts": {
    "start": "react-scripts start",
    "start:bienestar": "env-cmd -f .env.bienestar react-scripts start",
    "start:mindcare": "env-cmd -f .env.mindcare react-scripts start",
    "start:global": "env-cmd -f .env.global react-scripts start",
    "build:bienestar": "env-cmd -f .env.bienestar react-scripts build",
    "build:mindcare": "env-cmd -f .env.mindcare react-scripts build",
    "build:global": "env-cmd -f .env.global react-scripts build"
  },
  "devDependencies": {
    "env-cmd": "^10.1.0"
  }
}
```

## 🌐 Configuración de API Client

### 4. **Cliente HTTP Configurado por Tenant**

```javascript
// src/utils/apiClient.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
const TENANT_ID = process.env.REACT_APP_TENANT_ID;

// Crear instancia de axios configurada
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    // Importante: asegurar que Host header coincida con el tenant
    'Host': process.env.REACT_APP_CLINIC_DOMAIN,
  },
});

// Interceptor para añadir token de autenticación
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(`auth_token_${TENANT_ID}`);
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar respuestas
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token inválido - logout automático
      localStorage.removeItem(`auth_token_${TENANT_ID}`);
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 5. **Servicio de Autenticación por Tenant**

```javascript
// src/services/authService.js
import apiClient from '../utils/apiClient';

const TENANT_ID = process.env.REACT_APP_TENANT_ID;

class AuthService {
  // Login específico por tenant
  async login(email, password) {
    try {
      const response = await apiClient.post('/api/auth/login/', {
        email,
        password
      });

      const { token, user } = response.data;
      
      // Guardar token con identificador de tenant
      localStorage.setItem(`auth_token_${TENANT_ID}`, token);
      localStorage.setItem(`user_data_${TENANT_ID}`, JSON.stringify(user));
      
      return { token, user };
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error de autenticación');
    }
  }

  // Registro (solo para pacientes en tenants)
  async register(userData) {
    if (TENANT_ID === 'public') {
      throw new Error('El registro no está disponible en el admin global');
    }

    try {
      const response = await apiClient.post('/api/auth/register/', userData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error de registro');
    }
  }

  // Logout
  logout() {
    localStorage.removeItem(`auth_token_${TENANT_ID}`);
    localStorage.removeItem(`user_data_${TENANT_ID}`);
  }

  // Obtener usuario actual
  getCurrentUser() {
    const userData = localStorage.getItem(`user_data_${TENANT_ID}`);
    return userData ? JSON.parse(userData) : null;
  }

  // Verificar si está autenticado
  isAuthenticated() {
    return !!localStorage.getItem(`auth_token_${TENANT_ID}`);
  }
}

export default new AuthService();
```

### 6. **Hook para Información del Tenant**

```javascript
// src/hooks/useTenant.js
import { useMemo } from 'react';

export const useTenant = () => {
  const tenantInfo = useMemo(() => {
    const tenantId = process.env.REACT_APP_TENANT_ID;
    const clinicName = process.env.REACT_APP_CLINIC_NAME;
    const apiBaseUrl = process.env.REACT_APP_API_BASE_URL;
    const isGlobalAdmin = tenantId === 'public';

    return {
      tenantId,
      clinicName,
      apiBaseUrl,
      isGlobalAdmin,
      // URLs disponibles según el tenant
      availableRoutes: isGlobalAdmin 
        ? ['/admin', '/clinics', '/domains'] 
        : ['/dashboard', '/appointments', '/patients', '/professionals', '/chat']
    };
  }, []);

  return tenantInfo;
};
```

## 🚀 Ejemplo de Uso en Componentes

### 7. **Componente de Login Adaptativo**

```javascript
// src/components/Login.jsx
import React, { useState } from 'react';
import authService from '../services/authService';
import { useTenant } from '../hooks/useTenant';

const Login = () => {
  const [credentials, setCredentials] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { clinicName, isGlobalAdmin } = useTenant();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await authService.login(credentials.email, credentials.password);
      
      // Redireccionar según el tipo de tenant
      window.location.href = isGlobalAdmin ? '/admin' : '/dashboard';
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h1>Iniciar Sesión</h1>
      <h2>{clinicName}</h2>
      
      {error && <div className="error">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={credentials.email}
          onChange={(e) => setCredentials({...credentials, email: e.target.value})}
          required
        />
        <input
          type="password"
          placeholder="Contraseña"
          value={credentials.password}
          onChange={(e) => setCredentials({...credentials, password: e.target.value})}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Iniciando sesión...' : 'Ingresar'}
        </button>
      </form>

      {/* Mostrar registro solo en tenants, no en admin global */}
      {!isGlobalAdmin && (
        <p>
          ¿No tienes cuenta? <a href="/register">Regístrate aquí</a>
        </p>
      )}
    </div>
  );
};

export default Login;
```

### 8. **Componente de Dashboard Adaptativo**

```javascript
// src/components/Dashboard.jsx
import React, { useEffect, useState } from 'react';
import apiClient from '../utils/apiClient';
import { useTenant } from '../hooks/useTenant';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { clinicName, isGlobalAdmin } = useTenant();

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        if (isGlobalAdmin) {
          // Para admin global: obtener estadísticas de clínicas
          const response = await apiClient.get('/api/admin/stats/');
          setData(response.data);
        } else {
          // Para tenants: obtener estadísticas de la clínica
          const response = await apiClient.get('/api/appointments/stats/');
          setData(response.data);
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [isGlobalAdmin]);

  if (loading) return <div>Cargando...</div>;

  return (
    <div className="dashboard">
      <h1>Dashboard - {clinicName}</h1>
      
      {isGlobalAdmin ? (
        // Dashboard para admin global
        <div>
          <h2>Gestión de Clínicas</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Total Clínicas</h3>
              <p>{data?.total_clinics || 0}</p>
            </div>
            <div className="stat-card">
              <h3>Dominios Activos</h3>
              <p>{data?.active_domains || 0}</p>
            </div>
          </div>
        </div>
      ) : (
        // Dashboard para tenants
        <div>
          <h2>Panel de Control de la Clínica</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Citas Hoy</h3>
              <p>{data?.appointments_today || 0}</p>
            </div>
            <div className="stat-card">
              <h3>Pacientes Total</h3>
              <p>{data?.total_patients || 0}</p>
            </div>
            <div className="stat-card">
              <h3>Profesionales</h3>
              <p>{data?.total_professionals || 0}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
```

## 🎯 Comandos de Desarrollo

### 9. **Ejecutar Frontend para Cada Clínica**

```bash
# Desarrollar para Clínica Bienestar
npm run start:bienestar
# Acceder desde: http://bienestar.localhost:3000

# Desarrollar para Clínica MindCare  
npm run start:mindcare
# Acceder desde: http://mindcare.localhost:3000

# Desarrollar para Admin Global
npm run start:global
# Acceder desde: http://localhost:3000
```

### 10. **Despliegue por Clínica**

```bash
# Build para cada clínica
npm run build:bienestar
npm run build:mindcare
npm run build:global

# Servir builds específicos
serve -s build-bienestar -l 3001
serve -s build-mindcare -l 3002
serve -s build-global -l 3000
```

## 🔒 Consideraciones de Seguridad

### 11. **Validaciones Importantes**

```javascript
// src/utils/tenantValidation.js
export const validateTenantAccess = (userTenant, requiredTenant) => {
  if (userTenant !== requiredTenant) {
    throw new Error('Acceso no autorizado a este tenant');
  }
};

// En cada llamada API crítica
const response = await apiClient.get('/api/sensitive-data/');
validateTenantAccess(response.data.tenant_id, process.env.REACT_APP_TENANT_ID);
```

## 📱 URLs de Acceso Final

```
🌐 Admin Global:     http://localhost:3000        → localhost:8000 (backend)
🏥 Clínica Bienestar: http://bienestar.localhost:3001 → bienestar.localhost:8000 (backend)  
🧠 Clínica MindCare:  http://mindcare.localhost:3002  → mindcare.localhost:8000 (backend)
```

## ✅ Checklist de Implementación

- [ ] Configurar archivos `.env` por clínica
- [ ] Modificar `package.json` con scripts específicos
- [ ] Implementar `apiClient.js` con configuración por tenant
- [ ] Crear `authService.js` con storage por tenant
- [ ] Implementar hook `useTenant()`
- [ ] Adaptar componentes para mostrar diferente contenido según tenant
- [ ] Configurar archivo `hosts` del sistema
- [ ] Probar login y funcionalidades en cada dominio

¡Con esta configuración tendrás un frontend completamente multi-tenant que se adapta automáticamente a cada clínica! 🚀