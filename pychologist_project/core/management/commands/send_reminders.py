from django.core.management.base import BaseCommand
from datetime import timedelta
from django.utils import timezone
from therapy.models import TherapySession
from notification.notification_service import NotificationService

class Command(BaseCommand):
    help = 'Envía recordatorios de sesiones próximas'

    def handle(self, *args, **kwargs):
        # Busca sesiones en las próximas 24 horas
        upcoming_sessions = TherapySession.objects.filter(
            scheduled_at__gte=timezone.now(),
            scheduled_at__lte=timezone.now() + timedelta(hours=24)
        )

        for session in upcoming_sessions:
            NotificationService.send_session_reminder(session)
            self.stdout.write(f"Recordatorio enviado para sesión {session.id}")