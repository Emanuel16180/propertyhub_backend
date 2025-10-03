# Guía Definitiva de Integración Frontend para Multi-Tenancy (Psico SAS)

## 1. Arquitectura y Separación de Mundos
- **Admin Público:** Solo para gestión global (clínicas, dominios, usuarios globales). No accedas a APIs de clínicas desde aquí.
- **Clínica (Tenant):** Cada subdominio (ej: bienestar.localhost) tiene su propio backend, APIs y admin.

## 2. Configuración de Orígenes (CORS)
- El backend acepta cualquier subdominio de localhost y cualquier puerto.
- Puedes desarrollar y probar en cualquier subdominio: `http://bienestar.localhost:5174`, `http://mindcare.localhost:5173`, etc.

## 3. Configuración del Frontend
### .env Ejemplo para Vite/React
```
VITE_API_BASE_URL=http://bienestar.localhost:8000
```
- Cambia el subdominio según la clínica que estés desarrollando.

## 4. Acceso a APIs
- **Solo accede a endpoints de la clínica:**
  - Ejemplo: `GET http://bienestar.localhost:8000/api/professionals/`
- **No accedas a endpoints del admin público desde el frontend.**

## 5. Autenticación
- Usa el endpoint de login de la clínica:
  - `POST http://bienestar.localhost:8000/api/auth/login/`
- Guarda el token y úsalo en el header:
  - `Authorization: Token <token>`

## 6. Ejemplo de Cliente Axios
```js
// src/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  withCredentials: true,
});

export default api;
```

## 7. Ejemplo de Hook para Login
```js
// src/hooks/useLogin.js
import api from '../api';

export const useLogin = () => async (email, password) => {
  const res = await api.post('/api/auth/login/', { email, password });
  return res.data;
};
```

## 8. Pruebas y Debug
- Accede a tu frontend en el subdominio correcto.
- Verifica que las peticiones van al backend de la clínica.
- Si ves error de CORS, revisa el subdominio y puerto.

## 9. URLs Clave
- Admin público: `http://localhost:8000/admin/`
- Admin clínica: `http://bienestar.localhost:8000/admin/`
- API clínica: `http://bienestar.localhost:8000/api/`

---
**Recuerda:** Cada clínica es un mundo separado. El frontend debe apuntar solo a su propio backend.
