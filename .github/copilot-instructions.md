# Psico SAS SP1 - Psychology Practice Management System

## Project Overview
Django REST API + Django Channels for a psychology practice management system with patient appointments, real-time chat, and professional profiles. Built for deployment on cloud platforms with PostgreSQL and Redis.

## Architecture & Key Components

### Apps Structure
- **`apps.authentication`**: Token-based auth, password reset with email templates
- **`apps.users`**: Custom user model with patient/professional/admin types, profile management
- **`apps.professionals`**: Psychologist profiles, specializations, working hours, public listings
- **`apps.appointments`**: Booking system with availability management, time slots, conflicts validation
- **`apps.chat`**: Real-time WebSocket chat tied to appointments using Django Channels

### Custom User Model
Uses `AUTH_USER_MODEL = 'users.CustomUser'` with:
- Three user types: `patient`, `professional`, `admin`
- Built-in fields: CI (cedula), phone, gender, date_of_birth, profile_picture
- Email as USERNAME_FIELD, auto-generated username from email
- Related models: PatientProfile, ProfessionalProfile

### Critical Business Logic
- **Appointment validation**: Checks psychologist availability, blocked dates, time conflicts
- **Time slot generation**: Dynamic slots based on professional's session_duration (default 60min)
- **Availability system**: Weekly schedules + JSON field for blocked specific dates
- **Real-time chat**: WebSocket authentication via token query param for mobile clients

## Development Patterns

### Serializer Conventions
- Separate serializers for create/update/read operations (e.g., `AppointmentCreateSerializer`)
- Public vs private data exposure (e.g., `ProfessionalPublicSerializer`)
- Custom validation methods that check business rules beyond field validation

### Permission Patterns
```python
# Custom permissions for resource ownership
class IsOwnerOrPsychologist(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (obj.patient == request.user or obj.psychologist == request.user)
```

### ViewSet Filtering
- User-type based querysets: patients see their appointments, professionals see theirs
- Query params for filtering: `status`, `date_from`, `date_to`, `specialization`, `city`
- No pagination on availability endpoints (`pagination_class = None`)

## Database & Models

### Key Relationships
- User → ProfessionalProfile (OneToOne)
- User → PatientProfile (OneToOne) 
- ProfessionalProfile → Specialization (ManyToMany)
- Appointment: patient + psychologist + date/time (unique_together constraint)
- PsychologistAvailability: weekly recurring + blocked_dates JSON field

### Time Handling
- Timezone: `America/La_Paz`
- Language: `es-es` (Spanish Bolivia)
- Time validation prevents past dates, checks availability windows

## WebSocket & Real-time Features

### Chat System
- WebSocket URL: `ws/chat/{appointment_id}/`
- Dual authentication: SessionAuth (web) → TokenAuth (mobile) middleware stack
- Custom `TokenAuthMiddleware` extracts token from query string for mobile clients

### Channel Layers
Currently uses `InMemoryChannelLayer` - change to Redis for production:
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {"hosts": [("redis-url", 6379)]},
    },
}
```

## Management Commands

### Data Population
```bash
python manage.py create_specializations     # Create psychology specializations
python manage.py populate_db               # Generate fake patients/psychologists  
python manage.py create_availability       # Set working hours for psychologists
```

### Development Workflow
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput   # For deployment
python manage.py runserver                 # Development
daphne config.asgi:application             # Production ASGI
```

## Configuration & Environment

### Required Environment Variables
```bash
SECRET_KEY=""
DEBUG=False
ALLOWED_HOSTS="domain.com,localhost"
DATABASE_URL="postgresql://..."
```

### CORS Configuration
Pre-configured for Vercel frontend deployment:
- `psico-admin-sp1-despliegue-front.vercel.app`
- Local development ports: 3000, 5173, 8080

### Email Integration
Gmail SMTP configured for password reset emails using custom template at `templates/registration/password_reset_email.html`

## API Patterns

### Authentication Flow
1. `POST /api/auth/register/` - Patient registration only
2. `POST /api/auth/login/` - Returns user data + token
3. Include token in headers: `Authorization: Token <token>`

### Key Endpoints
- `GET/POST /api/appointments/appointments/` - CRUD with automatic validation
- `GET /api/appointments/search-psychologists/?date=YYYY-MM-DD` - Available professionals
- `GET /api/professionals/` - Public directory with filters
- `GET/POST /api/appointments/availability/` - Psychologist schedule management

### Error Handling
- Custom validation messages in Spanish
- Business rule violations return 400 with descriptive errors
- Permission checks return 403 with clear messages

## Testing & Quality

### Database Seeding
Uses Faker library with Spanish locale for realistic test data. Normalizes text to remove accents/tildes from generated names for clean usernames/emails.

### Common Issues
- User type validation: Use `professional` not `psychologist` in filters
- Time slot conflicts: Always validate against existing appointments
- WebSocket auth: Mobile clients need token in query string, not headers
- CI validation: 7-10 digits regex, unique constraint

## Deployment Notes
- Uses WhiteNoise for static files
- PostgreSQL via dj-database-url
- Gunicorn + Daphne for HTTP + WebSocket serving
- Configured for Vercel/Railway/Heroku deployment patterns