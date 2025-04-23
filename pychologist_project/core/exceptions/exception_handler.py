from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response
import logging
from rest_framework.exceptions import ValidationError
from .custom_exceptions import EntityNotFoundError, BusinessLogicError, InvalidOperationError
from core.api_response.response import ApiResponse
from datetime import datetime
from core.api_response.response import DjangoResponseWrapper

audit_logger = logging.getLogger('audit_logger')

def custom_exception_handler(exc, context):
    """
    Custom exception handler that formats all errors using ApiResponse format.
    """
    # Get default DRF response
    response = exception_handler(exc, context)
    
    request = context.get('request')
    user = request.user if request and request.user.is_authenticated else None
    user_id = getattr(user, 'id', None)
    ip_address = request.META.get('REMOTE_ADDR') if request else 'unknown'
    view = context.get('view')
    view_name = view.__class__.__name__ if view else 'unknown'
    
    log_context = {
        'view': view_name,
        'user_id': user_id,
        'ip': ip_address,
        'exception': str(exc),
        'timestamp': datetime.now().isoformat()
    }

    if isinstance(exc, ValidationError):
        audit_logger.warning(
            "ValidationError - View: %(view)s, User: %(user_id)s, IP: %(ip)s, Error: %(exception)s",
            log_context
        )

        return DjangoResponseWrapper.bad_request(
            data={"errors": exc.detail},
            message="Validation error", 
        )
    elif isinstance(exc, EntityNotFoundError):
        audit_logger.warning(
            "EntityNotFoundError - View: %(view)s, User: %(user_id)s, IP: %(ip)s, Error: %(exception)s",
            log_context
        )
        return DjangoResponseWrapper.not_found(
            data=None,
            entity=exc.entity_name,
            param='ID',
            value=exc.entity_id
        )

    elif isinstance(exc, (BusinessLogicError, ValueError)):
        audit_logger.error(
            "BusinessLogicError - View: %(view)s, User: %(user_id)s, IP: %(ip)s, Error: %(exception)s",
            log_context,
            exc_info=True
        )
        return DjangoResponseWrapper.bad_request(message=str(exc))
    elif isinstance(exc, InvalidOperationError):
        audit_logger.error(
            "InvalidOperationError - View: %(view)s, User: %(user_id)s, IP: %(ip)s, Error: %(exception)s",
            log_context,
            exc_info=True
        )
        return DjangoResponseWrapper.conflict(str(exc))

    elif response is None:
        audit_logger.critical(
            "UnhandledException - View: %(view)s, User: %(user_id)s, IP: %(ip)s, Error: %(exception)s",
            log_context,
            exc_info=True
        )
        return DjangoResponseWrapper.internal_server_error(
            message="An unexpected error occurred. Please try again later."
        )

    # Format existing DRF responses with ApiResponse
    if response is not None:
        response.data = Response(
            data=response.data if hasattr(response, 'data') else None,
        )
    
    return response