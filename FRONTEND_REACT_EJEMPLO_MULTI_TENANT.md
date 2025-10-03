# Ejemplo Moderno de Frontend React para Multi-Tenancy

Este ejemplo asume que tu frontend corre en un subdominio (ej: bienestar.localhost:5174) y se conecta solo al backend de su clínica.

## 1. Configuración .env
```
VITE_API_BASE_URL=http://bienestar.localhost:8000
```

## 2. Cliente Axios
```js
// src/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  withCredentials: true,
});

export default api;
```

## 3. Hook de Autenticación
```js
// src/hooks/useLogin.js
import api from '../api';

export const useLogin = () => async (email, password) => {
  const res = await api.post('/api/auth/login/', { email, password });
  localStorage.setItem('token', res.data.token);
  return res.data;
};
```

## 4. Ejemplo de Componente de Login
```jsx
// src/components/LoginForm.jsx
import { useState } from 'react';
import { useLogin } from '../hooks/useLogin';

export default function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const login = useLogin();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login(email, password);
      window.location.reload();
    } catch (err) {
      setError('Credenciales inválidas');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" required />
      <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Contraseña" required />
      <button type="submit">Iniciar sesión</button>
      {error && <div style={{color:'red'}}>{error}</div>}
    </form>
  );
}
```

## 5. Ejemplo de Llamada a la API de la Clínica
```js
// src/services/professionals.js
import api from '../api';

export const getProfessionals = async () => {
  const token = localStorage.getItem('token');
  const res = await api.get('/api/professionals/', {
    headers: { Authorization: `Token ${token}` }
  });
  return res.data;
};
```

## 6. Prueba y Debug
- Accede a tu frontend en el subdominio correcto.
- Verifica que las peticiones van al backend de la clínica.
- Si ves error de CORS, revisa el subdominio y puerto.

---
**Solo accede a APIs del backend de la clínica correspondiente.**
