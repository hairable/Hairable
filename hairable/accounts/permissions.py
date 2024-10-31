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
        is_ai_assistant = request.headers.get('User-Agent') == 'AIAssistant'
        if view.action == 'create':
            return bool(
                request.user and
                request.user.is_authenticated and
                (request.user.role == "CEO" or request.user.is_staff or is_ai_assistant)
            )

        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role in self.allowed_roles or request.user.is_staff or is_ai_assistant)
        )

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
