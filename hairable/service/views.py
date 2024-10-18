from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Service, Reservation, Customer, SalesReport, Category
from .serializers import ServiceSerializer, ReservationSerializer, CustomerSerializer, SalesReportSerializer, CategorySerializer
from stores.models import Store, StoreStaff, WorkCalendar
from datetime import datetime
from dateutil import parser
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

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
            return Response({'detail': '매장을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

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
        assigned_designer_user_id = request.data.get('assigned_designer')

        try:
            reservation_time = parser.parse(request.data.get('reservation_time'))
            store = Store.objects.get(id=store_id)
            service = Service.objects.get(id=service_id, store=store)
            assigned_designer = StoreStaff.objects.get(user_id=assigned_designer_user_id, store=store)

            # 서비스의 소요 시간 계산
            duration = service.duration
            end_time = reservation_time + duration

            # 해당 디자이너의 기존 예약 확인
            overlapping_reservations = Reservation.objects.filter(
                assigned_designer=assigned_designer,
                reservation_time__lt=end_time,
                reservation_time__gt=reservation_time - duration
            )

            if overlapping_reservations.exists():
                return Response({'detail': '해당 시간에 이미 예약이 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)

            # 매니저도 같은 방식으로 확인
            if StoreStaff.objects.filter(user_id=assigned_designer_user_id, store=store, role='manager').exists():
                overlapping_reservations = Reservation.objects.filter(
                    assigned_designer__user_id=assigned_designer_user_id,
                    reservation_time__lt=end_time,
                    reservation_time__gt=reservation_time - duration
                )
                if overlapping_reservations.exists():
                    return Response({'detail': '해당 시간에 이미 예약이 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)
            # 디자이너의 근무 상태 확인
            work_calendar = WorkCalendar.objects.filter(
                staff=assigned_designer,
                date=reservation_time.date(),
                status='working'
            ).first()

            if not work_calendar:
                return Response({'detail': '해당 날짜에 디자이너가 근무하지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)

            # 예약 시간이 근무 시간 내에 있는지 확인
            if not (work_calendar.start_time <= reservation_time.time() <= work_calendar.end_time):
                return Response({'detail': '예약 시간이 디자이너의 근무 시간을 벗어났습니다.'}, status=status.HTTP_400_BAD_REQUEST)
            # 예약 생성
            return super().create(request, *args, **kwargs)
        except Store.DoesNotExist:
            return Response({'detail': '매장을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
        except Service.DoesNotExist:
            return Response({'detail': '해당 매장에 없는 서비스입니다.'}, status=status.HTTP_404_NOT_FOUND)
        except StoreStaff.DoesNotExist:
            return Response({'detail': '해당 매장에서 등록되지 않은 디자이너입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, parser.ParserError):
            return Response({'detail': '예약 시간 형식이 잘못되었습니다.'}, status=status.HTTP_400_BAD_REQUEST)

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
