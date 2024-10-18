from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'manager'

class IsDesigner(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'designer'
    
class IsStoreStaff(BasePermission):   #주석 : 권한 클래스 추가 (IsStoreStaff)
    def has_permission(self, request, view):
        return request.user and request.user.staff_roles.exists()

    def has_object_permission(self, request, view, obj):
        return request.user.staff_roles.filter(store=obj.store).exists()
    