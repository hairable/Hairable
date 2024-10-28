from rest_framework.permissions import BasePermission, SAFE_METHODS
from enum import Enum

class UserRole(Enum):
    CEO = "CEO"
    MANAGER = "manager"
    DESIGNER = "designer"
    STAFF = "staff"
    USER = "user"

class BaseRolePermission(BasePermission):
    allowed_roles = []
    
    def has_permission(self, request, view):
        is_ai_assistant = request.headers.get('User-Agent') == 'AIAssistant'
        return bool(
            request.user and 
            request.user.is_authenticated and
            (request.user.role in self.allowed_roles or 
             request.user.is_staff or
             is_ai_assistant)
        )
    
    def has_object_permission(self, request, view, obj):
        is_ai_assistant = request.headers.get('User-Agent') == 'AIAssistant'
        
        if hasattr(obj, 'ceo'):
            return obj.ceo == request.user or request.user.is_staff or is_ai_assistant
        if hasattr(obj, 'store'):
            return (
                obj.store.ceo == request.user or 
                request.user.staff_roles.filter(store=obj.store).exists() or
                request.user.is_staff or 
                is_ai_assistant
            )
        return False

class IsCEO(BaseRolePermission):
    allowed_roles = [UserRole.CEO.value]

class IsManager(BaseRolePermission):
    allowed_roles = [UserRole.MANAGER.value]

class IsDesigner(BaseRolePermission):
    allowed_roles = [UserRole.DESIGNER.value]

class IsStoreStaff(BaseRolePermission):
    allowed_roles = [UserRole.MANAGER.value, UserRole.DESIGNER.value, UserRole.STAFF.value, UserRole.CEO.value]