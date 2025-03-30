from .models import TherapyParticipant, TherapySession

class SessionService:

    def get_session_by_id(self, session_id):
        try:
            return TherapySession.objects.get(id=session_id)
        except TherapySession.DoesNotExist:
            return ValueError("Session Not Found")


    