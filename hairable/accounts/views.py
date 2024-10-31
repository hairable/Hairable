import re
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile
from .serializers import (
    UserSerializer,
    UserDetailSerializer,
    ResetPasswordEmailRequestSerializer,
    ChangePasswordSerializer,
    PublicProfileSerializer
)
from utils.email_verification import send_verification_email


# Create your views here.
User = get_user_model()

# GET: 회원 목록 조회, POST: 회원 가입
class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]
    

    def perform_create(self, serializer):
        user = serializer.save()
        send_verification_email(user, self.request)  # 이메일 인증 링크 전송

        # 토큰 생성
        refresh = RefreshToken.for_user(user)

        # 기존 직렬화된 데이터를 수정 가능한 딕셔너리로 변환
        response_data = dict(serializer.data)
        response_data["access"] = str(refresh.access_token)
        response_data["refresh"] = str(refresh)

        return Response(response_data, status=201)
    
@api_view(['GET'])
def verify_email(request, uidb64, token):
    try:
        # uidb64를 디코딩하여 사용자의 pk 가져오기
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        verification_link = request.build_absolute_uri(
        reverse('accounts:verify_email', kwargs={'uidb64': uid, 'token': token})
    )
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if not user.is_active:
            # 계정 활성화 처리
            user.is_active = True
            user.save()
            return Response({'message': '이메일 인증이 완료되었습니다.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': '계정이 이미 활성화되었습니다.'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': '유효하지 않은 링크입니다.'}, status=status.HTTP_400_BAD_REQUEST)
    
class UserUpdateDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    # 회원 정보 수정 (PUT)
    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserDetailSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "회원 정보가 성공적으로 수정되었습니다."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 회원 탈퇴 (DELETE)
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False  # 계정 비활성화
        user.save()
        return Response({"message": "회원탈퇴가 완료되었습니다."}, status=status.HTTP_204_NO_CONTENT)
    
    
# 자신의 프로필 Profile 조회(GET) 및 수정(PUT)
class ProfileAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer
    
    def get_object(self):
        user = self.request.user
        Profile.objects.get_or_create(user=user)
        return user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
# 다른 사용자의 프로필 조회 
class UserProfileAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = PublicProfileSerializer
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

        if not email: 
            return Response({'message': '이메일을 입력해 주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        try: 
            user = User.objects.get(email=email)
            # 이메일로 사용자 아이디 전송
            send_mail(
                'Hairable 아이디 찾기',
                f'당신의 아이디는 {user.username}입니다.',
                'latiger95@gmail.com',  # 발신자 이메일
                [email],
                fail_silently=False,
            )
            return Response({'message': '아이디 찾기 요청이 처리되었습니다. 이메일을 확인해주세요.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist: 
            return Response({'message': '등록된 이메일이 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
    
# POST: 분실시 비밀번호 이메일 인증 요청, PUT: 인증 완료 후 새 비밀번호로 변경
class ResetPasswordAPIView(APIView):
    def post(self, request):
        serializer = ResetPasswordEmailRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_link = request.build_absolute_uri(
                    reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )
                send_mail(
                    '비밀번호 재설정',  
                    f'링크를 클릭하여 비밀번호를 재설정 하세요: {reset_link}',  
                    'latiger95@gmail.com',  
                    [email],  
                    fail_silently=False
                )
                return Response({'message': '비밀번호 재설정 링크가 이메일로 전송되었습니다.'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'message': '등록된 이메일이 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 이메일 인증을 통한 비밀번호 재설정 (PUT 요청)
    def put(self, request, uidb64, token):
        new_password = request.data.get('new_password')

        if not new_password:
            return Response({'message': '새로운 비밀번호가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'message': '유효하지 않은 사용자입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        # 토큰 확인
        if default_token_generator.check_token(user, token):
            # 비밀번호 검증 및 설정
            if len(new_password) < 8 or not re.search(r'[0-9]', new_password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
                return Response({'message': '비밀번호는 최소 8자 이상이어야 하며, 숫자와 특수 문자를 포함해야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
            user.save()
            return Response({'message': '비밀번호가 성공적으로 재설정되었습니다.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': '유효하지 않은 토큰입니다.'}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            if not user.check_password(old_password):
                return Response({'message': '기존 비밀번호가 올바르지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            return Response({'message': '비밀번호가 성공적으로 변경되었습니다.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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