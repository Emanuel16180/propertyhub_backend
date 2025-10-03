# 🚀 Ejemplo Práctico: Frontend React Multi-Tenant

## 📁 Estructura de Proyecto Frontend

```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Header.jsx
│   │   │   ├── Navigation.jsx
│   │   │   └── Layout.jsx
│   │   ├── auth/
│   │   │   ├── Login.jsx
│   │   │   └── Register.jsx
│   │   ├── dashboard/
│   │   │   ├── GlobalDashboard.jsx
│   │   │   └── ClinicDashboard.jsx
│   │   └── appointments/
│   │       ├── AppointmentsList.jsx
│   │       └── CreateAppointment.jsx
│   ├── hooks/
│   │   ├── useTenant.js
│   │   ├── useAuth.js
│   │   └── useApi.js
│   ├── services/
│   │   ├── apiClient.js
│   │   ├── authService.js
│   │   └── appointmentService.js
│   ├── utils/
│   │   ├── constants.js
│   │   └── helpers.js
│   ├── App.jsx
│   └── index.js
├── .env.bienestar
├── .env.mindcare
├── .env.global
└── package.json
```

## 📝 Archivos de Configuración

### `.env.bienestar`
```env
REACT_APP_API_BASE_URL=http://bienestar.localhost:8000
REACT_APP_CLINIC_NAME=Clínica Bienestar
REACT_APP_CLINIC_DOMAIN=bienestar.localhost
REACT_APP_TENANT_ID=bienestar
REACT_APP_CLINIC_LOGO=/assets/bienestar-logo.png
REACT_APP_PRIMARY_COLOR=#28a745
```

### `.env.mindcare`
```env
REACT_APP_API_BASE_URL=http://mindcare.localhost:8000
REACT_APP_CLINIC_NAME=Clínica MindCare
REACT_APP_CLINIC_DOMAIN=mindcare.localhost
REACT_APP_TENANT_ID=mindcare
REACT_APP_CLINIC_LOGO=/assets/mindcare-logo.png
REACT_APP_PRIMARY_COLOR=#007bff
```

### `.env.global`
```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_CLINIC_NAME=Psico SAS - Admin Global
REACT_APP_CLINIC_DOMAIN=localhost
REACT_APP_TENANT_ID=public
REACT_APP_CLINIC_LOGO=/assets/global-logo.png
REACT_APP_PRIMARY_COLOR=#6f42c1
```

## 🔧 Servicios Base

### `src/services/apiClient.js`
```javascript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
const TENANT_ID = process.env.REACT_APP_TENANT_ID;
const CLINIC_DOMAIN = process.env.REACT_APP_CLINIC_DOMAIN;

// Configuración global de axios
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Interceptor para requests
apiClient.interceptors.request.use(
  (config) => {
    // Añadir token si existe
    const token = localStorage.getItem(`auth_token_${TENANT_ID}`);
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }

    // Asegurar que el Host header coincida con el tenant
    config.headers.Host = CLINIC_DOMAIN;

    // Log para debugging en desarrollo
    if (process.env.NODE_ENV === 'development') {
      console.log(`🌐 API Request [${TENANT_ID}]:`, {
        method: config.method.toUpperCase(),
        url: config.url,
        baseURL: config.baseURL,
        headers: config.headers
      });
    }

    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Interceptor para responses
apiClient.interceptors.response.use(
  (response) => {
    // Log para debugging en desarrollo
    if (process.env.NODE_ENV === 'development') {
      console.log(`✅ API Response [${TENANT_ID}]:`, {
        status: response.status,
        url: response.config.url,
        data: response.data
      });
    }
    return response;
  },
  (error) => {
    console.error(`❌ API Error [${TENANT_ID}]:`, error);

    // Manejo específico de errores
    if (error.response?.status === 401) {
      // Token inválido o expirado
      localStorage.removeItem(`auth_token_${TENANT_ID}`);
      localStorage.removeItem(`user_data_${TENANT_ID}`);
      
      // Redireccionar a login si no estamos ya ahí
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    } else if (error.response?.status === 403) {
      // Sin permisos
      console.error('Sin permisos para acceder a este recurso');
    } else if (error.response?.status === 404) {
      // Endpoint no encontrado
      console.error('Endpoint no encontrado - puede ser un problema de tenant');
    }

    return Promise.reject(error);
  }
);

export default apiClient;
```

### `src/services/authService.js`
```javascript
import apiClient from './apiClient';

const TENANT_ID = process.env.REACT_APP_TENANT_ID;

class AuthService {
  // Login
  async login(email, password) {
    try {
      const response = await apiClient.post('/api/auth/login/', {
        email,
        password
      });

      const { token, user } = response.data;
      
      // Validar que el usuario pertenece al tenant correcto
      if (TENANT_ID !== 'public' && user.tenant_id && user.tenant_id !== TENANT_ID) {
        throw new Error('Usuario no autorizado para esta clínica');
      }

      // Guardar datos con prefijo de tenant
      localStorage.setItem(`auth_token_${TENANT_ID}`, token);
      localStorage.setItem(`user_data_${TENANT_ID}`, JSON.stringify(user));
      
      return { token, user };
    } catch (error) {
      throw new Error(
        error.response?.data?.message || 
        error.response?.data?.error || 
        'Error de autenticación'
      );
    }
  }

  // Registro (solo para tenants)
  async register(userData) {
    if (TENANT_ID === 'public') {
      throw new Error('El registro no está disponible en el admin global');
    }

    try {
      const response = await apiClient.post('/api/auth/register/', {
        ...userData,
        tenant_id: TENANT_ID
      });
      
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.message || 
        error.response?.data?.error || 
        'Error de registro'
      );
    }
  }

  // Logout
  logout() {
    localStorage.removeItem(`auth_token_${TENANT_ID}`);
    localStorage.removeItem(`user_data_${TENANT_ID}`);
    window.location.href = '/login';
  }

  // Obtener usuario actual
  getCurrentUser() {
    const userData = localStorage.getItem(`user_data_${TENANT_ID}`);
    return userData ? JSON.parse(userData) : null;
  }

  // Verificar autenticación
  isAuthenticated() {
    const token = localStorage.getItem(`auth_token_${TENANT_ID}`);
    const user = this.getCurrentUser();
    return !!(token && user);
  }

  // Verificar si es admin
  isAdmin() {
    const user = this.getCurrentUser();
    return user?.is_staff || user?.is_superuser || false;
  }

  // Obtener token
  getToken() {
    return localStorage.getItem(`auth_token_${TENANT_ID}`);
  }
}

export default new AuthService();
```

## 🎣 Hooks Personalizados

### `src/hooks/useTenant.js`
```javascript
import { useMemo } from 'react';

export const useTenant = () => {
  const tenantInfo = useMemo(() => {
    const tenantId = process.env.REACT_APP_TENANT_ID;
    const clinicName = process.env.REACT_APP_CLINIC_NAME;
    const apiBaseUrl = process.env.REACT_APP_API_BASE_URL;
    const clinicDomain = process.env.REACT_APP_CLINIC_DOMAIN;
    const clinicLogo = process.env.REACT_APP_CLINIC_LOGO;
    const primaryColor = process.env.REACT_APP_PRIMARY_COLOR;
    const isGlobalAdmin = tenantId === 'public';

    // Configurar rutas disponibles según tenant
    const availableRoutes = isGlobalAdmin ? {
      dashboard: '/admin',
      clinics: '/clinics',
      domains: '/domains',
      users: '/global-users'
    } : {
      dashboard: '/dashboard',
      appointments: '/appointments',
      patients: '/patients',
      professionals: '/professionals',
      chat: '/chat',
      profile: '/profile'
    };

    // APIs disponibles según tenant
    const availableAPIs = isGlobalAdmin ? [
      '/api/admin/stats/',
      '/api/tenants/clinics/',
      '/api/tenants/domains/'
    ] : [
      '/api/auth/',
      '/api/users/',
      '/api/professionals/',
      '/api/appointments/',
      '/api/chat/'
    ];

    return {
      tenantId,
      clinicName,
      apiBaseUrl,
      clinicDomain,
      clinicLogo,
      primaryColor,
      isGlobalAdmin,
      availableRoutes,
      availableAPIs,
      // Función helper para generar URLs
      buildApiUrl: (endpoint) => `${apiBaseUrl}${endpoint}`,
      // Función helper para verificar si una API está disponible
      canAccessAPI: (endpoint) => availableAPIs.some(api => endpoint.startsWith(api))
    };
  }, []);

  return tenantInfo;
};
```

### `src/hooks/useAuth.js`
```javascript
import { useState, useEffect, useContext, createContext } from 'react';
import authService from '../services/authService';
import { useTenant } from './useTenant';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const { isGlobalAdmin } = useTenant();

  useEffect(() => {
    // Verificar autenticación al cargar
    const checkAuth = () => {
      if (authService.isAuthenticated()) {
        const currentUser = authService.getCurrentUser();
        setUser(currentUser);
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (email, password) => {
    const { user } = await authService.login(email, password);
    setUser(user);
    return user;
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    isAdmin: authService.isAdmin(),
    isGlobalAdmin,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de AuthProvider');
  }
  return context;
};
```

## 🧩 Componentes Principales

### `src/components/common/Header.jsx`
```javascript
import React from 'react';
import { useTenant } from '../../hooks/useTenant';
import { useAuth } from '../../hooks/useAuth';

const Header = () => {
  const { clinicName, clinicLogo, primaryColor, isGlobalAdmin } = useTenant();
  const { user, logout } = useAuth();

  const headerStyle = {
    backgroundColor: primaryColor,
    color: 'white',
    padding: '1rem',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  };

  return (
    <header style={headerStyle}>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        {clinicLogo && (
          <img 
            src={clinicLogo} 
            alt={clinicName} 
            style={{ height: '40px', marginRight: '1rem' }}
          />
        )}
        <h1>{clinicName}</h1>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {user && (
          <>
            <span>
              {isGlobalAdmin ? '👑 ' : '👤 '}
              {user.first_name} {user.last_name}
            </span>
            <button 
              onClick={logout}
              style={{
                background: 'rgba(255,255,255,0.2)',
                border: '1px solid white',
                color: 'white',
                padding: '0.5rem 1rem',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Cerrar Sesión
            </button>
          </>
        )}
      </div>
    </header>
  );
};

export default Header;
```

### `src/components/auth/Login.jsx`
```javascript
import React, { useState } from 'react';
import { useTenant } from '../../hooks/useTenant';
import { useAuth } from '../../hooks/useAuth';

const Login = () => {
  const [credentials, setCredentials] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { clinicName, primaryColor, isGlobalAdmin } = useTenant();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await login(credentials.email, credentials.password);
      
      // Redireccionar según tipo de tenant
      window.location.href = isGlobalAdmin ? '/admin' : '/dashboard';
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const containerStyle = {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    backgroundColor: '#f5f5f5'
  };

  const formStyle = {
    backgroundColor: 'white',
    padding: '2rem',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    width: '100%',
    maxWidth: '400px'
  };

  const buttonStyle = {
    backgroundColor: primaryColor,
    color: 'white',
    border: 'none',
    padding: '0.75rem 1.5rem',
    borderRadius: '4px',
    cursor: 'pointer',
    width: '100%',
    fontSize: '1rem'
  };

  return (
    <div style={containerStyle}>
      <div style={formStyle}>
        <h1 style={{ textAlign: 'center', marginBottom: '0.5rem' }}>
          Iniciar Sesión
        </h1>
        <h2 style={{ 
          textAlign: 'center', 
          color: primaryColor,
          marginBottom: '2rem',
          fontSize: '1.2rem'
        }}>
          {clinicName}
        </h2>
        
        {error && (
          <div style={{
            backgroundColor: '#ffebee',
            color: '#c62828',
            padding: '0.75rem',
            borderRadius: '4px',
            marginBottom: '1rem'
          }}>
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1rem' }}>
            <input
              type="email"
              placeholder="Email"
              value={credentials.email}
              onChange={(e) => setCredentials({...credentials, email: e.target.value})}
              required
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '1rem'
              }}
            />
          </div>
          
          <div style={{ marginBottom: '1.5rem' }}>
            <input
              type="password"
              placeholder="Contraseña"
              value={credentials.password}
              onChange={(e) => setCredentials({...credentials, password: e.target.value})}
              required
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '1rem'
              }}
            />
          </div>
          
          <button 
            type="submit" 
            disabled={loading}
            style={{
              ...buttonStyle,
              opacity: loading ? 0.7 : 1,
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? 'Iniciando sesión...' : 'Ingresar'}
          </button>
        </form>

        {/* Mostrar registro solo en tenants */}
        {!isGlobalAdmin && (
          <p style={{ textAlign: 'center', marginTop: '1rem' }}>
            ¿No tienes cuenta? {' '}
            <a 
              href="/register" 
              style={{ color: primaryColor, textDecoration: 'none' }}
            >
              Regístrate aquí
            </a>
          </p>
        )}
      </div>
    </div>
  );
};

export default Login;
```

### `src/App.jsx`
```javascript
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './hooks/useAuth';
import { useTenant } from './hooks/useTenant';

import Header from './components/common/Header';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import GlobalDashboard from './components/dashboard/GlobalDashboard';
import ClinicDashboard from './components/dashboard/ClinicDashboard';

// Componente para rutas protegidas
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div>Cargando...</div>;
  }

  return isAuthenticated ? children : <Navigate to="/login" />;
};

// Componente principal de rutas
const AppRoutes = () => {
  const { isGlobalAdmin } = useTenant();
  const { isAuthenticated } = useAuth();

  return (
    <Router>
      <div className="app">
        {isAuthenticated && <Header />}
        
        <Routes>
          <Route path="/login" element={<Login />} />
          
          {/* Rutas para admin global */}
          {isGlobalAdmin ? (
            <>
              <Route 
                path="/admin" 
                element={
                  <ProtectedRoute>
                    <GlobalDashboard />
                  </ProtectedRoute>
                } 
              />
              <Route path="/" element={<Navigate to="/admin" />} />
            </>
          ) : (
            <>
              {/* Rutas para tenants */}
              <Route path="/register" element={<Register />} />
              <Route 
                path="/dashboard" 
                element={
                  <ProtectedRoute>
                    <ClinicDashboard />
                  </ProtectedRoute>
                } 
              />
              <Route path="/" element={<Navigate to="/dashboard" />} />
            </>
          )}
          
          {/* Ruta 404 */}
          <Route path="*" element={<div>Página no encontrada</div>} />
        </Routes>
      </div>
    </Router>
  );
};

// App principal
function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}

export default App;
```

## 🚀 Scripts de Desarrollo

### `package.json`
```json
{
  "name": "psico-frontend-multitenant",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "axios": "^1.3.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "start:bienestar": "env-cmd -f .env.bienestar react-scripts start",
    "start:mindcare": "env-cmd -f .env.mindcare react-scripts start", 
    "start:global": "env-cmd -f .env.global react-scripts start",
    "build": "react-scripts build",
    "build:bienestar": "env-cmd -f .env.bienestar react-scripts build",
    "build:mindcare": "env-cmd -f .env.mindcare react-scripts build",
    "build:global": "env-cmd -f .env.global react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "devDependencies": {
    "env-cmd": "^10.1.0",
    "react-scripts": "5.0.1"
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
```

## 🎯 Comandos de Uso

```bash
# Instalar dependencias
npm install

# Desarrollo - Clínica Bienestar
npm run start:bienestar
# → http://bienestar.localhost:3000

# Desarrollo - Clínica MindCare  
npm run start:mindcare
# → http://mindcare.localhost:3000

# Desarrollo - Admin Global
npm run start:global
# → http://localhost:3000

# Builds de producción
npm run build:bienestar
npm run build:mindcare
npm run build:global
```

¡Con esta configuración tendrás un frontend React completamente funcional y multi-tenant! 🎉