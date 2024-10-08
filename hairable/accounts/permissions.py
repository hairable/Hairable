from rest_framework.permissions import BasePermission

class IsCEO(BasePermission):
    def has_permission(self, request, view):
        # CEO 권한을 확인
        return request.user and request.user.role == 'CEO'
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'ceo'):
            return obj.ceo == request.user
        return False  # 주석: CEO와 관련 없는 객체에 대해서는 권한 거부
    
class IsAnyCEO(BasePermission):
    def has_permission(self, request, view):
        # 모든 CEO는 스토어를 생성할 수 있도록 허용
        return request.user and request.user.role == 'CEO'