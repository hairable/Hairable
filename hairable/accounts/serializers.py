from .models import User
from rest_framework import serializers
from django.core.exceptions import ValidationError
import re
from .models import User, Profile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "password", "phone", "birthday", "gender", "introduction")
        extra_kwargs = {
            'password': {'write_only': True}  # 비밀번호는 작성 시에만 사용하고, 응답에는 포함되지 않도록 설정.
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            password=validated_data.get('password'),
            phone=validated_data.get('phone'),
            birthday=validated_data.get('birthday'),
            gender=validated_data.get('gender'),
            introduction=validated_data.get('introduction'),
        )
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('store', 'profile_image', 'introduction', 'specialty')
        
class UserDetailSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    
    class Meta:
        model = User
        fields = ('username', 'email', 'profile', 'phone', 'gender')
        
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        profile = instance.profile
        
        # 회원 정보 수정 시 내용 반영
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.save()

        # 프로필 수정
        profile.store = profile_data.get('store', profile.store)
        profile.profile_image = profile_data.get('profile_image', profile.profile_image)
        profile.introduction = profile_data.get('introduction', profile.introduction)
        profile.specialty = profile_data.get('specialty', profile.specialty)
        profile.save()
        
        return instance
        
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_new_password(self, value):
        if len(value) < 8 or not re.search(r'[0-9]', value) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError("비밀번호는 최소 8자 이상이어야 하며, 숫자와 특수 문자를 포함해야 합니다.")
        return value
    

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)