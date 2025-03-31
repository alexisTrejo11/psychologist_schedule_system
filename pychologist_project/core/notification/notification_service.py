from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
from django.template.loader import render_to_string

class NotificationService:
    @staticmethod
    def send_email(subject, message, recipient_list, html_message=None):
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            html_message=html_message,
            fail_silently=False,
        )

    @staticmethod
    def send_sms(message, to_phone_number):
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_phone_number
        )

    @staticmethod
    def send_session_reminder(session):
        # Datos compartidos
        context = {
            'therapist_name': session.therapist.user.get_full_name(),
            'patient_name': session.patient.user.get_full_name(),
            'scheduled_at': session.scheduled_at.strftime('%d/%m/%Y %H:%M'),
        }

        # Renderiza el HTML para el terapeuta
        therapist_html_message = render_to_string('email_reminder_therapist.html', context)

        # Envía notificación al terapeuta
        NotificationService.send_email(
            subject=f"Recordatorio: Sesión con {session.patient.user.get_full_name()}",
            message=f"Tienes una sesión programada para {session.scheduled_at}.",
            recipient_list=[session.therapist.user.email],
            html_message=therapist_html_message,
        )
        NotificationService.send_sms(
            message=f"Recordatorio: Sesión con {session.patient.user.get_full_name()} a las {session.scheduled_at}.",
            to_phone_number=session.therapist.phone_number,
        )

        # Renderiza el HTML para el paciente
        patient_html_message = render_to_string('email_reminder_patient.html', context)

        # Envía notificación al paciente
        NotificationService.send_email(
            subject=f"Recordatorio: Sesión con {session.therapist.user.get_full_name()}",
            message=f"Tienes una sesión programada para {session.scheduled_at}.",
            recipient_list=[session.patient.user.email],
            html_message=patient_html_message,
        )
        NotificationService.send_sms(
            message=f"Recordatorio: Sesión con {session.therapist.user.get_full_name()} a las {session.scheduled_at}.",
            to_phone_number=session.patient.phone_number,
        )