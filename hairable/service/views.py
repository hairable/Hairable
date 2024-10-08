from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Service, Reservation, Customer, SalesReport
from .serializers import ServiceSerializer, ReservationSerializer, CustomerSerializer, SalesReportSerializer, CategorySerializer
from stores.models import Category

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def recommend_designer(self, request):
        service_id = request.data.get('service_id')
        reservation_time = request.data.get('reservation_time')
        try:
            service = Service.objects.get(pk=service_id)
            available_designers = [
                designer for designer in service.available_designers.filter(role='designer')
                if not Reservation.objects.filter(assigned_designer=designer, reservation_time=reservation_time).exists()
            ]
            if available_designers:
                return Response({'recommended_designer': available_designers[0].user.username}, status=status.HTTP_200_OK)
            return Response({'detail': 'No available designer found.'}, status=status.HTTP_404_NOT_FOUND)
        except Service.DoesNotExist:
            return Response({'detail': 'Service not found.'}, status=status.HTTP_404_NOT_FOUND)


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

class SalesReportViewSet(viewsets.ModelViewSet):
    queryset = SalesReport.objects.all()
    serializer_class = SalesReportSerializer
    permission_classes = [IsAdminUser]

# 카테고리 뷰셋 정의
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
