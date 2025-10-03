# Credenciales y URLs para Testing Multi-Tenant

## 1. Admin Público
- URL: http://localhost:8000/admin/
- Usuario: superusuario global (creado con `create_public_superuser`)
- Acceso: Solo gestión de clínicas y dominios

## 2. Clínica Bienestar
- URL Admin: http://bienestar.localhost:8000/admin/
- URL API: http://bienestar.localhost:8000/api/
- Usuario: admin de clínica (creado con `tenant_command createsuperuser --schema=bienestar`)

## 3. Ejemplo de Login API
```
POST http://bienestar.localhost:8000/api/auth/login/
{
  "email": "admin@bienestar.com",
  "password": "tu_password"
}
```

## 4. Ejemplo de Llamada API
```
GET http://bienestar.localhost:8000/api/professionals/
Headers: Authorization: Token <token>
```

## 5. Debug
- Si ves error de CORS, revisa el subdominio y puerto.
- Si ves 404 en la API, revisa que estés en el subdominio correcto.

---
**Recuerda:** Cada clínica tiene su propio mundo y credenciales. El admin público no accede a datos de clínicas.
