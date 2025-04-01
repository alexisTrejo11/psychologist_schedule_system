from rest_framework.views import APIView
from rest_framework.response import Response
from .models import AuditLog
from .serializers import AuditLogSerializer

class AuditLogListView(APIView):
    def get(self, request):
        logs = AuditLog.objects.all().order_by('-timestamp')
        serializer = AuditLogSerializer(logs, many=True)
        return Response(serializer.data)