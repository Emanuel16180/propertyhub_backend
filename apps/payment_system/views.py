# apps/payment_system/views.py

import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from apps.appointments.models import Appointment
from apps.appointments.serializers import AppointmentCreateSerializer
from django.shortcuts import get_object_or_404
from apps.users.models import CustomUser
import logging

# Configurar el logger
logger = logging.getLogger(__name__)

# Configurar Stripe con la clave secreta
stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateCheckoutSessionView(APIView):
    """
    Vista para crear una sesión de pago en Stripe.
    Proceso:
    1. Valida y crea una cita preliminar en estado 'pending'
    2. Crea la sesión de pago en Stripe
    3. Retorna el sessionId para redirigir al usuario
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        psychologist_id = data.get('psychologist')
        
        # 1. Validar y crear una cita preliminar en estado 'pending'
        # Usamos el AppointmentCreateSerializer que ya tiene toda la lógica de validación de horarios
        serializer = AppointmentCreateSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Creamos la cita pero aún no está pagada
        appointment = serializer.save(status='pending', is_paid=False)

        # 2. Obtener el precio de la consulta
        psychologist = get_object_or_404(CustomUser, id=psychologist_id)
        
        # Verificar que el psicólogo tenga perfil profesional
        if not hasattr(psychologist, 'professional_profile'):
            appointment.delete()  # Limpiar la cita creada
            return Response({
                'error': 'Este usuario no tiene un perfil profesional configurado.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        fee = psychologist.professional_profile.consultation_fee
        
        if not fee or fee <= 0:
            appointment.delete()  # Limpiar la cita creada
            return Response({
                'error': 'Este profesional no tiene una tarifa configurada.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 3. Crear la sesión de pago en Stripe
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',  # Puedes cambiar a 'bob' para bolivianos
                            'product_data': {
                                'name': f'Consulta con {psychologist.get_full_name()}',
                                'description': f'Cita agendada para el {appointment.appointment_date} a las {appointment.start_time}',
                            },
                            'unit_amount': int(fee * 100),  # Stripe maneja los montos en centavos
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                # URLs a las que Stripe redirigirá al usuario
                success_url=f"http://{request.get_host()}/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"http://{request.get_host()}/payment-cancelled",
                # Guardamos el ID de nuestra cita para saber qué actualizar después
                metadata={
                    'appointment_id': appointment.id,
                    'patient_id': request.user.id,
                    'psychologist_id': psychologist_id
                }
            )
            
            logger.info(f"Sesión de pago creada: {checkout_session.id} para cita {appointment.id}")
            
            return Response({
                'sessionId': checkout_session.id,
                'appointment_id': appointment.id,
                'amount': fee,
                'currency': 'USD'
            })

        except stripe.error.StripeError as e:
            # Si Stripe falla, borramos la cita preliminar para liberar el horario
            appointment.delete()
            logger.error(f"Error de Stripe: {str(e)}")
            return Response({
                'error': f'Error del servicio de pagos: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            # Error general
            appointment.delete()
            logger.error(f"Error general en checkout: {str(e)}")
            return Response({
                'error': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StripeWebhookView(APIView):
    """
    Vista para recibir eventos de Stripe.
    Maneja la confirmación de pagos exitosos.
    """
    permission_classes = [permissions.AllowAny]  # No requiere token, Stripe la llama directamente

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            # Payload inválido
            logger.error(f"Payload inválido en webhook: {str(e)}")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            # Firma inválida
            logger.error(f"Firma inválida en webhook: {str(e)}")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Manejar el evento checkout.session.completed
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            appointment_id = session.get('metadata', {}).get('appointment_id')

            if appointment_id:
                try:
                    appointment = Appointment.objects.get(id=appointment_id)
                    # ¡Pago exitoso! Actualizamos la cita
                    appointment.is_paid = True
                    appointment.status = 'confirmed'
                    appointment.save()
                    
                    logger.info(f"Pago confirmado para cita {appointment_id}")
                    
                    # Aquí podrías añadir lógica adicional como:
                    # - Enviar email de confirmación
                    # - Crear notificación push
                    # - Actualizar estadísticas
                    
                except Appointment.DoesNotExist:
                    # La cita no fue encontrada, loguear este error
                    logger.error(f"Cita {appointment_id} no encontrada en webhook")
            else:
                logger.warning("Webhook recibido sin appointment_id en metadata")
        
        # Manejar cancelaciones de pago
        elif event['type'] == 'checkout.session.expired':
            session = event['data']['object']
            appointment_id = session.get('metadata', {}).get('appointment_id')
            
            if appointment_id:
                try:
                    appointment = Appointment.objects.get(id=appointment_id)
                    # Liberar el horario si la sesión expira
                    appointment.delete()
                    logger.info(f"Cita {appointment_id} eliminada por sesión expirada")
                except Appointment.DoesNotExist:
                    pass
        
        return Response(status=status.HTTP_200_OK)


class PaymentStatusView(APIView):
    """
    Vista para verificar el estado de un pago específico
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(
                id=appointment_id,
                patient=request.user
            )
            
            return Response({
                'appointment_id': appointment.id,
                'is_paid': appointment.is_paid,
                'status': appointment.status,
                'appointment_date': appointment.appointment_date,
                'start_time': appointment.start_time,
                'psychologist': appointment.psychologist.get_full_name(),
                'consultation_fee': appointment.consultation_fee
            })
            
        except Appointment.DoesNotExist:
            return Response({
                'error': 'Cita no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)


class GetStripePublicKeyView(APIView):
    """
    Vista para obtener la clave pública de Stripe (necesaria para el frontend)
    """
    permission_classes = [permissions.AllowAny]  # Clave pública, puede ser accesible
    
    def get(self, request):
        return Response({
            'publicKey': settings.STRIPE_PUBLISHABLE_KEY
        })
