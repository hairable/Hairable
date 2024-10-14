from rest_framework import viewsets
from .models import Supplier, Supply
from .serializers import SupplierSerializer, SupplySerializer, SupplyCreateSerializer
from rest_framework.permissions import IsAuthenticated  # 주석: 인증 권한 추가

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]  # 주석: 인증된 사용자만 접근 가능하도록 설정

class SupplyViewSet(viewsets.ModelViewSet):
    queryset = Supply.objects.all()
    serializer_class = SupplySerializer
    permission_classes = [IsAuthenticated]  # 주석: 인증된 사용자만 접근 가능하도록 설정

    def get_serializer_class(self):
        if self.action == 'create':
            return SupplyCreateSerializer
        return SupplySerializer
