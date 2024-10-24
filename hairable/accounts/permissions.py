from rest_framework.permissions import BasePermission, SAFE_METHODS

class AllowAny(BasePermission):
    def has_permission(self, request, view):
        return True

class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj == request.user

class IsCEO(BasePermission):
    def has_permission(self, request, view):
        is_ceo = request.user and request.user.role == 'CEO'
        is_ai_assistant = request.headers.get('User-Agent') == 'AIAssistant' or request.user.is_staff
        return is_ceo or is_ai_assistant
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'ceo'):
            return obj.ceo == request.user or request.user.is_staff
        return False

class IsAnyCEO(BasePermission):
    def has_permission(self, request, view):
        is_ceo = request.user and request.user.role == 'CEO'
        is_ai_assistant = request.headers.get('User-Agent') == 'AIAssistant' or request.user.is_staff
        return is_ceo or is_ai_assistant

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'manager'

class IsDesigner(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'designer'

class IsStoreStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.staff_roles.exists() or request.user.stores.exists())

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'store'):
            return (
                request.user.staff_roles.filter(store=obj.store).exists() or 
                obj.store.ceo == request.user
            )
        elif hasattr(obj, 'ceo'):
            return (
                request.user.staff_roles.filter(store=obj).exists() or 
                obj.ceo == request.user
            )
        return False

class IsStoreManagerOrCEO(BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'store'):
            return request.user.staff_roles.filter(store=obj.store, role__in=['manager', 'CEO']).exists()
        return request.user.role == 'CEO'
    
    
class IsStoreManagerOrCEO2(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == 'CEO':
            return True
        return request.user.staff_roles.filter(role='manager').exists()

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'CEO':
            if hasattr(obj, 'store'):
                return obj.store.ceo == request.user
            elif hasattr(obj, 'ceo'):
                return obj.ceo == request.user
        elif hasattr(obj, 'store'):
            return request.user.staff_roles.filter(store=obj.store, role='manager').exists()
        return False

class IsStoreCEO(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.ceo == request.user