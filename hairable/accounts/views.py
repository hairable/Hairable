from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.exceptions import TokenError
from .models import User
from .validators import validate_user_data
from .serializers import UserSerializer, UserProfileSerializer
# Create your views here.


class UserCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        rlt_message = validate_user_data(request.data)
        if len(rlt_message) > 0:
            return Response({"message": rlt_message}, status=400)


        user = User.objects.create_user(
            username = request.data.get("username"),
            email = request.data.get("email"),
            password =request.data.get("password"),
            phone = request.data.get("phone"),
            birthday = request.data.get("birthday"),
            gender = request.data.get("gender"),
            introduction = request.data.get("introduction"),
        )
        # user = User.objects.create_user(**request)

        refresh = RefreshToken.for_user(user) # 토큰 발급

        serializer = UserSerializer(user)
        response_dict = serializer.data
        response_dict["access"] = str(refresh.access_token)
        response_dict["refresh"] = str(refresh)
        return Response(response_dict) 


class UserProfileView(APIView):

    def get(self, request, username):
        user = User.objects.get(username=username)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)


