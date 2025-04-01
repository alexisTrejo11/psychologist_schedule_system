from drf_spectacular.utils import OpenApiTypes, extend_schema_field
from therapy.serializers import TherapySessionSerializer

@extend_schema_field(TherapySessionSerializer(many=True))
class TherapySessionsListResponseSchema():
    type = OpenApiTypes.OBJECT
    properties = {
        'success': {'type': 'boolean', 'description': 'Indica si la operación fue exitosa'},
        'message': {'type': 'string', 'description': 'Mensaje descriptivo de la respuesta'},
        'data': {
            'type': 'array',
            'items': TherapySessionSerializer(many=True),
            'description': 'Lista de sesiones de terapia',
        },
    }

@extend_schema_field(TherapySessionSerializer)
class TherapySessionResponseSchema():
    type = OpenApiTypes.OBJECT
    properties = {
        'success': {'type': 'boolean', 'description': 'Indica si la operación fue exitosa'},
        'message': {'type': 'string', 'description': 'Mensaje descriptivo de la respuesta'},
        'data': {
            'type': 'object',
            'properties': TherapySessionSerializer(),
            'description': 'Datos de la sesión de terapia',
        },
    }