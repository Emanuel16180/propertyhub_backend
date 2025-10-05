# 💳 SISTEMA DE PAGOS CON STRIPE - DOCUMENTACIÓN COMPLETA

## 🚀 FUNCIONALIDADES IMPLEMENTADAS

### ✅ Backend (Django) - COMPLETADO
1. **Integración completa con Stripe**
2. **Creación de sesiones de pago**
3. **Webhooks para confirmación automática**
4. **Modelo de transacciones**
5. **Endpoints RESTful**

### 🎯 ENDPOINTS DISPONIBLES

#### 1. **Obtener Clave Pública de Stripe**
```http
GET /api/payments/stripe-public-key/
Authorization: Token <user-token>
```

**Respuesta:**
```json
{
  "publicKey": "pk_test_51XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
}
```

#### 2. **Crear Sesión de Pago**
```http
POST /api/payments/create-checkout-session/
Authorization: Token <user-token>
Content-Type: application/json

{
  "psychologist": 123,
  "appointment_date": "2025-10-10",
  "start_time": "14:00",
  "appointment_type": "online",
  "reason_for_visit": "Consulta inicial"
}
```

**Respuesta Exitosa:**
```json
{
  "sessionId": "cs_test_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "appointment_id": 456,
  "amount": 150.00,
  "currency": "USD"
}
```

**Errores Posibles:**
```json
{
  "error": "Este profesional no tiene una tarifa configurada."
}
```

#### 3. **Verificar Estado de Pago**
```http
GET /api/payments/payment-status/456/
Authorization: Token <user-token>
```

**Respuesta:**
```json
{
  "appointment_id": 456,
  "is_paid": true,
  "status": "confirmed",
  "appointment_date": "2025-10-10",
  "start_time": "14:00:00",
  "psychologist": "Dr. María González",
  "consultation_fee": "150.00"
}
```

#### 4. **Webhook de Stripe** (Solo para Stripe)
```http
POST /api/payments/stripe-webhook/
Content-Type: application/json
Stripe-Signature: t=xxxxx,v1=xxxxx
```

## 🔧 CONFIGURACIÓN REQUERIDA

### 1. **Variables de Entorno (.env)**
```properties
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY="pk_test_51XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
STRIPE_SECRET_KEY="sk_test_51XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
STRIPE_WEBHOOK_SECRET="whsec_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

### 2. **Configuración en Stripe Dashboard**
1. **Crear cuenta en Stripe** → https://dashboard.stripe.com
2. **Obtener claves API** → Developers → API keys
3. **Configurar webhook** → Developers → Webhooks

**URL del Webhook:** `https://tu-dominio.com/api/payments/stripe-webhook/`

**Eventos a escuchar:**
- `checkout.session.completed`
- `checkout.session.expired`

## 🏗️ PROCESO DE PAGO

### **Flujo Completo:**

1. **Usuario selecciona psicólogo y horario**
2. **Frontend obtiene clave pública de Stripe**
   ```javascript
   const response = await fetch('/api/payments/stripe-public-key/')
   const { publicKey } = await response.json()
   ```

3. **Frontend crea sesión de pago**
   ```javascript
   const response = await fetch('/api/payments/create-checkout-session/', {
     method: 'POST',
     headers: {
       'Authorization': `Token ${userToken}`,
       'Content-Type': 'application/json'
     },
     body: JSON.stringify({
       psychologist: professionalId,
       appointment_date: '2025-10-10',
       start_time: '14:00',
       appointment_type: 'online',
       reason_for_visit: 'Consulta inicial'
     })
   })
   const { sessionId } = await response.json()
   ```

4. **Redirigir a Stripe Checkout**
   ```javascript
   const stripe = Stripe(publicKey)
   stripe.redirectToCheckout({ sessionId })
   ```

5. **Usuario completa el pago en Stripe**

6. **Stripe envía webhook confirmando pago**

7. **Backend actualiza cita automáticamente:**
   - `is_paid = True`
   - `status = 'confirmed'`

8. **Usuario es redirigido a página de éxito**

## 💻 CÓDIGO PARA EL FRONTEND

### **React/JavaScript Ejemplo:**

```javascript
import { loadStripe } from '@stripe/stripe-js'

// 1. Configurar Stripe
const getStripePublicKey = async () => {
  const response = await fetch('/api/payments/stripe-public-key/', {
    headers: {
      'Authorization': `Token ${localStorage.getItem('token')}`
    }
  })
  const { publicKey } = await response.json()
  return loadStripe(publicKey)
}

// 2. Función para procesar pago
const handlePayment = async (appointmentData) => {
  try {
    // Crear sesión de pago
    const response = await fetch('/api/payments/create-checkout-session/', {
      method: 'POST',
      headers: {
        'Authorization': `Token ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(appointmentData)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Error al crear la sesión de pago')
    }

    const { sessionId } = await response.json()
    
    // Redirigir a Stripe
    const stripe = await getStripePublicKey()
    const { error } = await stripe.redirectToCheckout({ sessionId })
    
    if (error) {
      console.error('Error al redirigir a Stripe:', error)
    }
  } catch (error) {
    console.error('Error en el proceso de pago:', error)
    alert('Error al procesar el pago: ' + error.message)
  }
}

// 3. Componente de ejemplo
const AppointmentBooking = () => {
  const bookAppointment = () => {
    const appointmentData = {
      psychologist: selectedPsychologist.id,
      appointment_date: selectedDate,
      start_time: selectedTime,
      appointment_type: 'online',
      reason_for_visit: reasonText
    }
    
    handlePayment(appointmentData)
  }

  return (
    <div>
      {/* Tu formulario de cita */}
      <button onClick={bookAppointment}>
        Reservar y Pagar Cita
      </button>
    </div>
  )
}
```

### **Páginas de Éxito y Cancelación:**

```javascript
// pages/PaymentSuccess.js
const PaymentSuccess = () => {
  const [appointment, setAppointment] = useState(null)
  
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const sessionId = urlParams.get('session_id')
    
    if (sessionId) {
      // Verificar estado del pago
      fetch(`/api/payments/payment-status/${appointmentId}/`, {
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        }
      })
      .then(res => res.json())
      .then(data => setAppointment(data))
    }
  }, [])

  return (
    <div>
      <h1>✅ ¡Pago Exitoso!</h1>
      {appointment && (
        <div>
          <p>Cita confirmada con {appointment.psychologist}</p>
          <p>Fecha: {appointment.appointment_date}</p>
          <p>Hora: {appointment.start_time}</p>
        </div>
      )}
    </div>
  )
}
```

## 🔐 SEGURIDAD

### **Medidas Implementadas:**
1. **Autenticación obligatoria** para crear pagos
2. **Validación de webhook** con firma de Stripe
3. **Logs detallados** de todas las transacciones
4. **Limpieza automática** de citas no pagadas
5. **Manejo de errores** completo

### **Validaciones:**
- ✅ Usuario autenticado
- ✅ Psicólogo tiene perfil profesional
- ✅ Tarifa configurada
- ✅ Horario disponible
- ✅ No conflictos de cita

## 📊 MONITOREO

### **Logs Disponibles:**
- Creación de sesiones de pago
- Confirmaciones de webhook
- Errores de Stripe
- Citas eliminadas por expiración

### **Métricas Recomendadas:**
- Tasa de conversión de pago
- Pagos fallidos
- Tiempo promedio de pago
- Reembolsos

## 🚀 PRÓXIMOS PASOS

### **Funcionalidades Adicionales:**
1. **Reembolsos automáticos**
2. **Pagos recurrentes**
3. **Múltiples métodos de pago**
4. **Reportes financieros**
5. **Notificaciones email/SMS**

¡El sistema de pagos está completamente implementado y listo para usar! 🎉