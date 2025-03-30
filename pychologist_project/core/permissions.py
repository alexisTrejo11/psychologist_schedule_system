from rest_framework.permissions import BasePermission

class IsTherapistOrAdmin(BasePermission):
  class IsTherapistOrAdmin(BasePermission):
    """
    Permite el acceso solo a usuarios con roles 'therapist' o 'admin'.
    """
    def has_permission(self, request, view):
        user_roles = getattr(request.user, 'roles', [])
        
        return 'therapist' in user_roles or 'admin' in user_roles