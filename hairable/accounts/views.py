from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
# Create your views here.
User = get_user_model()


# 로그인 API
class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': '아이디 또는 비밀번호가 잘못되었습니다.'}, status=status.HTTP_401_UNAUTHORIZED)

# 아이디 찾기(이메일)
class FindUsernameAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            return Response({'username': user.username}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': '등록된 이메일이 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
# 비밀번호 찾기
class ResetPasswordAPIView(APIView):
    def post(self, request):
        # 비밀번호 재설정 로직 작성 (이메일 전송 등)
        return Response({'message': '비밀번호 재설정 링크가 이메일로 전송되었습니다.'}, status=status.HTTP_200_OK)