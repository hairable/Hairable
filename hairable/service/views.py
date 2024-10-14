from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Service, Reservation, Customer, SalesReport
from .serializers import ServiceSerializer, ReservationSerializer, CustomerSerializer, SalesReportSerializer, CategorySerializer
from stores.models import Category, Store, StoreStaff

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        category_id = request.data.get('category')
        inventory_category_id = request.data.get('inventory_category')
        inventory_id = request.data.get('inventory')
        store_id = request.data.get('store')

        # 필수 항목 확인
        if not category_id or not inventory_category_id or not inventory_id or not store_id:
            return Response({"error": "서비스 등록을 위해 서비스 카테고리, 재고 카테고리, 매장이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return Response({'detail': 'Store not found.'}, status=status.HTTP_404_NOT_FOUND)

        # 슈퍼 호출 전에 서비스 생성 로직을 실행해 staff 추가
        response = super().create(request, *args, **kwargs)
        service = Service.objects.get(pk=response.data['id'])
        
        # 매장의 직원 중 해당 서비스 제공 가능한 직원들만 추가
        store_staff = StoreStaff.objects.filter(store=store, available_services=service)
        service.available_designers.set(store_staff)

        return response



class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        store_id = request.data.get('store_id')
        service_id = request.data.get('service')
        assigned_designer_id = request.data.get('assigned_designer')

        try:
            store = Store.objects.get(id=store_id)
            
            # 현재 로그인한 사용자가 해당 매장의 소유자인지 확인
            if store.ceo != request.user:
                return Response({'detail': 'You are not authorized to make a reservation for this store.'}, status=status.HTTP_403_FORBIDDEN)

            # 서비스가 해당 매장에서 제공되는지 확인
            service = Service.objects.get(id=service_id, store=store)

            if assigned_designer_id:
                assigned_designer = StoreStaff.objects.get(id=assigned_designer_id)

                # 배정된 디자이너가 해당 매장 소속인지 확인
                if assigned_designer.store != store:
                    return Response({'detail': 'The assigned designer must be from the same store as the service.'}, status=status.HTTP_400_BAD_REQUEST)

        except Store.DoesNotExist:
            return Response({'detail': 'Store not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Service.DoesNotExist:
            return Response({'detail': 'Service not found for the given store.'}, status=status.HTTP_404_NOT_FOUND)
        except StoreStaff.DoesNotExist:
            return Response({'detail': 'Designer not found for the given store.'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)


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
    permission_classes = [IsAuthenticated]

# 카테고리 뷰셋 정의
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    
    
