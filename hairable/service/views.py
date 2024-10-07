from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import ServiceCategory, Service
from .serializers import ServiceCategorySerializer, ServiceSerializer, ServiceCreateSerializer
from rest_framework.permissions import IsAuthenticated  # 주석: 인증된 사용자만 접근 가능하도록 추가

# Create your views here.

class ServiceCategoryViewSet(viewsets.ModelViewSet):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAuthenticated]  # 주석: 인증된 사용자만 접근 가능하도록 추가

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]  # 주석: 인증된 사용자만 접근 가능하도록 추가

    def create(self, request):
        serializer = ServiceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # 주석: 유효성 검사 실패 시 자동으로 예외 발생
        service = serializer.save()
        return Response(ServiceSerializer(service).data, status=status.HTTP_201_CREATED)
