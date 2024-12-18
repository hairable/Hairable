from .models import User
from rest_framework import serializers
from django.core.exceptions import ValidationError
import re
from .models import User, Profile
from stores.models import StoreStaff
from django.contrib.auth.password_validation import validate_password  # 주석: Django의 기본 비밀번호 검증기 사용

class ProfileSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    work_status = serializers.BooleanField()  # 근무 상태 (True: 근무중, False: 근무 안함)
    career_list = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False)  # 경력 목록
    certificate_list = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False)  # 자격증 목록
    position = serializers.CharField(source='user.staff_roles.role', read_only=True)  # stores의 StoreStaff 역할을 가져옴
    
    class Meta:
        model = Profile
        fields = ('store_name', 'profile_image', 'introduction', 'specialty', 'work_status', 'career_list', 'certificate_list', 'position')  # 추가 필드 포함

class PublicProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('profile_image', 'introduction', 'career_list', 'certificate_list')  # 추가 필드 포함


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)  # 프로필을 선택적으로 연결, required=False 사용
    workplace = serializers.CharField(source='profile.store.name', read_only=True)  # 근무지 추가
    position = serializers.CharField(source='profile.specialty', read_only=True)  # 직급(매장 내 직급) 추가
    work_status = serializers.BooleanField(source='profile.work_status', read_only=True)  # 근무 상태 추가
    password = serializers.CharField(validators=[validate_password], write_only = True)
    password_confirm = serializers.CharField(write_only = True) 
    class Meta:
        model = User
        fields = ("username", "email", "password", "password_confirm", "phone", "birthday", "gender", "introduction", "role", 'profile', 'workplace', 'position', 'work_status')
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return data
    
    def validate_role(self, value):
        if value not in ['CEO', 'user']:
            raise serializers.ValidationError("회원가입 시에는 'CEO' 또는 'user' 역할만 선택할 수 있습니다.")
        return value
    
    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            password=validated_data.get('password'),
            phone=validated_data.get('phone'),
            birthday=validated_data.get('birthday'),
            gender=validated_data.get('gender'),
            introduction=validated_data.get('introduction'),
            is_active=False,
            role=validated_data.get('role'),
        )
        
        if profile_data:
            Profile.objects.create(user=user, **profile_data)
        
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    workplace = serializers.CharField(source='profile.store.name', read_only=True) 
    position = serializers.CharField(source='profile.specialty', read_only=True) 
    work_status = serializers.BooleanField(source='profile.work_status', read_only=True)
    career_list = serializers.ListField(source='profile.career_list', read_only=True)
    certificate_list = serializers.ListField(source='profile.certificate_list', read_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'profile', 'phone', 'gender', 'workplace', 'position', 'work_status', 'career_list', 'certificate_list')  # 'profile' 필드를 추가

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        profile, created = Profile.objects.get_or_create(user=instance)


        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.save()

        if profile_data:
            profile.store = profile_data.get('store', profile.store)
            profile.profile_image = profile_data.get('profile_image', profile.profile_image)
            profile.introduction = profile_data.get('introduction', profile.introduction)
            profile.specialty = profile_data.get('specialty', profile.specialty)
            profile.work_status = profile_data.get('work_status', profile.work_status)
            profile.career_list = profile_data.get('career_list', profile.career_list)
            profile.certificate_list = profile_data.get('certificate_list', profile.certificate_list)
            profile.save()

        return instance




class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("등록된 이메일이 없습니다.")
        return value
    

class ResetPasswordConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])  # 주석: 비밀번호 유효성 검사 추가

    def validate_new_password(self, value):
        if len(value) < 8 or not re.search(r'[0-9]', value) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("비밀번호는 최소 8자 이상이어야 하며, 숫자와 특수 문자를 포함해야 합니다.")
        return value

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])  # 주석: 비밀번호 유효성 검사 추가

    def validate_new_password(self, value):
        if len(value) < 8 or not re.search(r'[0-9]', value) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("비밀번호는 최소 8자 이상이어야 하며, 숫자와 특수 문자를 포함해야 합니다.")
        return value

    

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)