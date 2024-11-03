from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response


class AttachTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = request.session.get('auth_token')
        if token:
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    
    def process_response(self, request, response):
        if isinstance(response, (JsonResponse, Response)):
            if hasattr(response, 'data') and isinstance(response.data, dict) and 'access' in response.data:
                request.session['auth_token'] = response.data['access']
        return response