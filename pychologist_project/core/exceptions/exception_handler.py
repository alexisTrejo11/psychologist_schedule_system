from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response
import logging
from rest_framework.exceptions import ValidationError
from .custom_exceptions import EntityNotFoundError, BusinessLogicError, InvalidOperationError
from core.api_response.response import ApiResponse
from datetime import datetime

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
        return Response(
            ApiResponse.format_response(
                data={"errors": exc.detail},
                success=False,
                message="Validation error"
            ),
            status=status.HTTP_400_BAD_REQUEST
        )

    elif isinstance(exc, EntityNotFoundError):
        audit_logger.warning(
            "EntityNotFoundError - View: %(view)s, User: %(user_id)s, IP: %(ip)s, Error: %(exception)s",
            log_context
        )
        return Response(
            ApiResponse.format_response(
                data=None,
                success=False,
                message=str(exc)
            ),
            status=status.HTTP_404_NOT_FOUND
        )

    elif isinstance(exc, (BusinessLogicError, ValueError)):
        audit_logger.error(
            "BusinessLogicError - View: %(view)s, User: %(user_id)s, IP: %(ip)s, Error: %(exception)s",
            log_context,
            exc_info=True
        )
        return Response(
            ApiResponse.format_response(
                data=None,
                success=False,
                message=str(exc)
            ),
            status=status.HTTP_400_BAD_REQUEST
        )

    elif isinstance(exc, InvalidOperationError):
        audit_logger.error(
            "InvalidOperationError - View: %(view)s, User: %(user_id)s, IP: %(ip)s, Error: %(exception)s",
            log_context,
            exc_info=True
        )
        return Response(
            ApiResponse.format_response(
                data=None,
                success=False,
                message=str(exc)
            ),
            status=status.HTTP_409_CONFLICT
        )

    elif response is None:
        audit_logger.critical(
            "UnhandledException - View: %(view)s, User: %(user_id)s, IP: %(ip)s, Error: %(exception)s",
            log_context,
            exc_info=True
        )
        return Response(
            ApiResponse.format_response(
                data=None,
                success=False,
                message="Internal server error"
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Format existing DRF responses with ApiResponse
    if response is not None:
        response.data = ApiResponse.format_response(
            data=response.data if hasattr(response, 'data') else None,
            success=False,
            message=getattr(exc, 'message', str(exc))
        )
    
    return response