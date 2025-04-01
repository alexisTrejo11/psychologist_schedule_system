class EntityNotFoundError(Exception):
    """
    Custom exception for cases where an entity is not found.
    """
    def __init__(self, entity_name: str, entity_id: int = None):
        self.entity_name = entity_name
        self.entity_id = entity_id
        message = f"{entity_name} no encontrado"
        if entity_id:
            message += f" con ID: {entity_id}"
        super().__init__(message)


class BusinessLogicError(Exception):
    """
    Custom exception for business logic errors.
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class InvalidOperationError(Exception):
    """
    Custom exception for invalid operations.
    """
    def __init__(self, operation: str, details: str = None):
        self.operation = operation
        self.details = details
        message = f"Operación inválida: {operation}"
        if details:
            message += f". Detalles: {details}"
        super().__init__(message)