# Sistema de Calificaciones (CU-34) - Documentación de API

## Endpoints Implementados

### 1. Crear Reseña
**POST** `/api/professionals/reviews/create/`

**Descripción**: Permite a un paciente crear una reseña para una cita completada.

**Autenticación**: Requerida (Token)
**Permisos**: Solo pacientes, solo citas completadas propias, una reseña por cita

**Body de ejemplo**:
```json
{
    "appointment": 48,
    "rating": 5,
    "comment": "Excelente profesional, muy empática y comprensiva."
}
```

**Respuesta exitosa**:
```json
{
    "id": 1,
    "professional": 2,
    "patient": 15,
    "patient_name": "Apolonia Gutierrez",
    "appointment": 48,
    "rating": 5,
    "comment": "Excelente profesional, muy empática y comprensiva.",
    "created_at": "2025-10-02T18:25:00Z"
}
```

### 2. Ver Reseñas de un Profesional
**GET** `/api/professionals/{professional_id}/reviews/`

**Descripción**: Lista todas las reseñas de un profesional específico (vista pública).

**Autenticación**: No requerida
**Permisos**: Público

**Respuesta de ejemplo**:
```json
{
    "professional_id": 2,
    "total_reviews": 4,
    "average_rating": 5.00,
    "reviews": [
        {
            "id": 11,
            "professional": 2,
            "patient": 38,
            "patient_name": "Florentina Garcia",
            "appointment": 98,
            "rating": 5,
            "comment": "Muy buena experiencia, profesional comprometida con sus pacientes.",
            "created_at": "2025-10-02T18:25:15Z"
        },
        {
            "id": 10,
            "professional": 2,
            "patient": 38,
            "patient_name": "Silvia Fabra",
            "appointment": 89,
            "rating": 5,
            "comment": "Profesional muy capacitada, me ha ayudado mucho en mi crecimiento personal.",
            "created_at": "2025-10-02T18:25:15Z"
        }
    ]
}
```

## Validaciones Implementadas

### Permisos de Seguridad
- ✅ Solo pacientes pueden crear reseñas
- ✅ Solo pueden reseñar sus propias citas
- ✅ Solo citas con estado 'completed'
- ✅ Una reseña por cita (unique constraint)
- ✅ Asignación automática de paciente y profesional

### Validaciones de Datos
- ✅ Rating: 1-5 estrellas (validadores Django)
- ✅ Comentario: opcional, texto libre
- ✅ Cita debe existir y pertenecer al usuario

## Funcionalidades Automáticas

### Actualización de Calificaciones
- ✅ Al crear una reseña, se recalcula automáticamente el `average_rating` y `total_reviews` del profesional
- ✅ Al eliminar una reseña, se recalcula automáticamente
- ✅ Redondeo a 2 decimales para mejor presentación

### Campos Calculados en ProfessionalProfile
- `average_rating`: Promedio de todas las reseñas (0.00 - 5.00)
- `total_reviews`: Número total de reseñas recibidas

## Casos de Uso Cubiertos

1. **Paciente crea reseña**: Después de una cita completada
2. **Vista pública de reseñas**: Cualquier persona puede ver las reseñas de un profesional
3. **Actualización automática**: Las calificaciones se mantienen actualizadas
4. **Seguridad**: Solo el paciente que tuvo la cita puede reseñarla
5. **Integridad**: Una cita solo puede ser reseñada una vez

## Estado Actual

- ✅ 15 reseñas de ejemplo creadas
- ✅ 10 profesionales con calificaciones calculadas
- ✅ Sistema completamente funcional
- ✅ Listo para integración con frontend

## Próximos Pasos para Frontend

1. **Formulario de Reseña**: Mostrar a pacientes sus citas completadas sin reseña
2. **Vista de Reseñas**: Mostrar reseñas en el perfil público del profesional
3. **Filtros**: Ordenar profesionales por calificación
4. **Validación UI**: Mensajes de error para casos no permitidos