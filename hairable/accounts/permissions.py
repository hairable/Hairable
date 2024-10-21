from rest_framework.permissions import BasePermission

class IsCEO(BasePermission):
    def has_permission(self, request, view):
        # CEO 권한을 확인하거나 AI Assistant가 특정 작업을 수행할 수 있도록 허용
        is_ceo = request.user and request.user.role == 'CEO'
        
        # AI Assistant의 요청일 경우 확인
        is_ai_assistant = request.headers.get('User-Agent') == 'AIAssistant' or request.user.is_staff  # AI가 직원으로 등록된 경우 허용

        return is_ceo or is_ai_assistant
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'ceo'):
            return obj.ceo == request.user or request.user.is_staff  # AI는 Staff 권한으로 매장 데이터 접근 허용
        return False  # 주석: CEO와 관련 없는 객체에 대해서는 권한 거부
    
class IsAnyCEO(BasePermission):
    def has_permission(self, request, view):
        # 모든 CEO는 스토어를 생성할 수 있도록 허용하거나 AI 요청일 경우 허용
        is_ceo = request.user and request.user.role == 'CEO'
        is_ai_assistant = request.headers.get('User-Agent') == 'AIAssistant' or request.user.is_staff
        return is_ceo or is_ai_assistant