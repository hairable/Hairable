from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, UserDetailSerializer
from rest_framework import generics
from django.contrib.auth.hashers import make_password
# Create your views here.
User = get_user_model()

# GET: 회원 목록 조회, POST: 회원 가입
class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        response_data = serializer.data
        response_data["access"] = str(refresh.access_token)
        response_data["refresh"] = str(refresh)
        return Response(response_data, status=201)

# 자신의 프로필 Profile 조회(GET) 및 수정(PUT)
class ProfileAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer
    
    def get_object(self):
        return self.request.user

# 다른 사용자의 프로필 조회 
class ProfileAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]  # 로그인된 회원만 접근 가능

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
    
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()  # 토큰을 블랙리스트에 추가하여 무효화
            return Response({"message": "성공적으로 로그아웃되었습니다."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "로그아웃 실패. 유효하지 않은 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST)