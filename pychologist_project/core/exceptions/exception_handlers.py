from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response
import logging
from .custom_exceptions import EntityNotFoundError, BusinessLogicError, InvalidOperationError


audit_logger = logging.getLogger('audit_logger')

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    request = context.get('request')
    user = request.user if request and request.user.is_authenticated else None
    ip_address = request.META.get('REMOTE_ADDR') if request else 'unknown'
    view = context.get('view')
    view_name = view.__class__.__name__ if view else 'unknown'

    if isinstance(exc, EntityNotFoundError):
        audit_logger.warning(
            f"EntityNotFoundError en vista {view_name}: {str(exc)}, Usuario: {user}, IP: {ip_address}"
        )
        response = Response(
            {"error": str(exc)},
            status=status.HTTP_404_NOT_FOUND
        )
    elif isinstance(exc, BusinessLogicError):
        audit_logger.error(
            f"BusinessLogicError en vista {view_name}: {str(exc)}, Usuario: {user}, IP: {ip_address}",
            exc_info=True
        )
        response = Response(
            {"error": str(exc)},
            status=status.HTTP_400_BAD_REQUEST
        )
    elif isinstance(exc, InvalidOperationError):
        audit_logger.error(
            f"InvalidOperationError en vista {view_name}: {str(exc)}, Usuario: {user}, IP: {ip_address}",
            exc_info=True
        )
        response = Response(
            {"error": str(exc)},
            status=status.HTTP_409_CONFLICT 
        )
    else:
        audit_logger.error(
            f"Excepción no manejada en vista {view_name}: {str(exc)}, Usuario: {user}, IP: {ip_address}",
            exc_info=True
        )
        response = Response(
            {"error": "Ocurrió un error interno. Por favor, intenta más tarde."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response