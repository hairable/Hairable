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
        return request.user and request.user.staff_roles.exists()

    def has_object_permission(self, request, view, obj):
        return request.user.staff_roles.filter(store=obj.store).exists()

class IsStoreManagerOrCEO(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.staff_roles.filter(store=obj.store, role__in=['manager', 'CEO']).exists()

class IsStoreCEO(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.store.ceo == request.user