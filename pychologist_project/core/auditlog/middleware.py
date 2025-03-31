import json
from django.utils.deprecation import MiddlewareMixin
from .models import AuditLog

class AuditLogMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                request_data = json.loads(request.body.decode('utf-8'))
            except Exception:
                request_data = {}
        else:
            request_data = {}

        request.audit_data = {
            'action': self._get_action(request.method),
            'resource': request.path,
            'data': request_data,
            'ip_address': self._get_client_ip(request),
        }

    def process_response(self, request, response):
        if hasattr(request, 'audit_data'):
            audit_data = request.audit_data
            user = request.user if request.user.is_authenticated else None

            AuditLog.objects.create(
                user=user,
                action=audit_data['action'],
                resource=audit_data['resource'],
                data=audit_data['data'],
                ip_address=audit_data['ip_address'],
                status_code=response.status_code,
            )

        return response

    def _get_action(self, method):
        """Map HTTP method based on the action."""
        mapping = {
            'GET': 'READ',
            'POST': 'CREATE',
            'PUT': 'UPDATE',
            'PATCH': 'UPDATE',
            'DELETE': 'DELETE',
        }
        return mapping.get(method, 'UNKNOWN')

    def _get_client_ip(self, request):
        """Get User IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip