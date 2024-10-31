from rest_framework.permissions import BasePermission
from enum import Enum

class UserRole(Enum):
    CEO = "CEO"
    manager = "manager"
    desginer = "designer"
    user = "user"

class UserRolePermission(BasePermission):
    _cached_roles = {}

    def __init__(self, *roles):
        role_key = frozenset(
            role if isinstance(role, UserRole) else UserRole(role) for role in roles
        )
        if role_key not in self._cached_roles:
            self._cached_roles[role_key] = {role.value for role in role_key}
        self.allowed_roles = self._cached_roles[role_key]

    def has_permission(self, request, view):
        # 사용자가 인증되어 있는지 확인
        if not request.user.is_authenticated:
            return False
            
        # view에서 지정한 required_role과 사용자의 role이 일치하는지 확인
        required_role = getattr(view, 'required_role', None)
        if required_role is None:
            return True
            
        return request.user.role == required_role

    def has_object_permission(self, request, view, obj):
        is_ai_assistant = request.headers.get('User-Agent') == 'AIAssistant'
        
        if hasattr(obj, 'store'):
            return (
                obj.store.ceo == request.user or
                request.user.staff_roles.filter(store=obj.store, role__in=self.allowed_roles).exists() or
                request.user.is_staff or
                is_ai_assistant
            )

        if hasattr(obj, 'ceo'):
            return obj.ceo == request.user or request.user.is_staff or is_ai_assistant
        return False
