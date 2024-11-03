from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response
import json

class AttachTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = request.session.get('auth_token')
        if token:
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    
    def process_response(self, request, response):
        if isinstance(response, (JsonResponse, Response)):
            try:
                if isinstance(response, Response):
                    data = response.data
                else:
                    data = json.loads(response.content.decode())
                
                if isinstance(data, dict) and 'access' in data:
                    request.session['auth_token'] = data['access']
                    # 세션 쿠키 설정
                    if not settings.DEBUG:
                        response.cookies['sessionid'].update({
                            'secure': True,
                            'httponly': True,
                            'samesite': 'Lax',
                            'domain': '.hairable.co.kr'
                        })
            except (json.JSONDecodeError, AttributeError):
                pass
        return response