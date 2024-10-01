from rest_framework.permissions import BasePermission

class IsCEO(BasePermission):
    def has_permission(self, request, view):
        # CEO 권한을 확인
        return request.user and request.user.role == 'CEO'
    
    def has_object_permission(self, request, view, obj):
        # 수정 또는 삭제 요청 시, CEO인지 확인
        return obj.ceo == request.user
    
class IsAnyCEO(BasePermission):
    def has_permission(self, request, view):
        # 모든 CEO는 스토어를 생성할 수 있도록 허용
        return request.user and request.user.role == 'CEO'