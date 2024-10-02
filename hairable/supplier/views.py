from rest_framework import viewsets
from .models import Supplier, Supply
from .serializers import SupplierSerializer, SupplySerializer, SupplyCreateSerializer

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class SupplyViewSet(viewsets.ModelViewSet):
    queryset = Supply.objects.all()
    serializer_class = SupplySerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return SupplyCreateSerializer
        return SupplySerializer
