from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Service, Reservation, Customer, SalesReport, Category
from .serializers import ServiceSerializer, ReservationSerializer, CustomerSerializer, SalesReportSerializer, CategorySerializer
from stores.models import Store, StoreStaff, WorkCalendar
from dateutil import parser
import logging
from django.db.models import Q
from django.db.models import Sum
from django.utils.dateparse import parse_date
from django.db import transaction
from django.db.models.functions import TruncMonth, TruncHour, TruncDay
import calendar
from django.db.models import F



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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = serializer.validated_data['service']
        assigned_designer = serializer.validated_data['assigned_designer']
        reservation_time = serializer.validated_data['reservation_time']

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
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
    def list(self, request, *args, **kwargs):
        query = request.query_params.get('query', '')
        queryset = self.queryset.filter(
            Q(customer__name__icontains=query) |
            Q(customer__phone_number__icontains=query) |
            Q(assigned_designer__user__username__icontains=query)
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    # 예약 수정 및 처리
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        reservation = self.get_object()
        new_status = request.data.get('status')
        new_date = request.data.get('new_date')

        if new_status not in ['예약 중', '예약 대기', '예약 취소', '방문 완료']:
            return Response({'error': '잘못된 상태입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_status == '예약 취소' and reservation.status != '예약 대기':
            return Response({'error': '예약 대기 상태만 취소할 수 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_date and reservation.status != '예약 중':
            return Response({'error': '예약 중 상태만 날짜를 변경할 수 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_date:
            try:
                new_date = parser.parse(new_date)
                reservation.reservation_time = new_date
            except ValueError:
                return Response({'error': '잘못된 날짜 형식입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        old_status = reservation.status
        reservation.status = new_status
        reservation.save()

        try:
            if new_status == '방문 완료' and old_status != '방문 완료':
                self.update_sales_report(reservation)
        except Exception as e:
            # 로그에 오류 기록
            logger.error(f"Sales report update failed: {str(e)}")
            # 상태는 변경되었지만 매출 보고서 업데이트에 실패했음을 클라이언트에 알림
            return Response({'message': '예약 상태가 변경되었지만, 매출 보고서 업데이트에 실패했습니다.'}, status=status.HTTP_200_OK)

        return Response({'message': '예약이 성공적으로 수정되었습니다.'})


    @transaction.atomic
    def update_sales_report(self, reservation):
        try:
            report_date = reservation.reservation_time.date()
            store = reservation.service.store
            report, created = SalesReport.objects.get_or_create(
                store=store,
                date=report_date,
                defaults={'total_revenue': 0, 'total_expenses': 0, 'net_profit': 0}
            )

            service_price = reservation.service.price
            inventory_cost = sum(item.inventory_item.cost * item.quantity for item in reservation.service.serviceinventory_set.all())
            
            report.total_revenue += service_price
            report.total_expenses += inventory_cost
            report.net_profit += (service_price - inventory_cost)

            report.save()
        except Exception as e:
            logger.error(f"Failed to update sales report: {str(e)}")
            raise

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        query = request.query_params.get('query', '')
        queryset = self.queryset.filter(
            Q(name__icontains=query) | Q(phone_number__icontains=query)
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)





class SalesReportViewSet(viewsets.ModelViewSet):
    queryset = SalesReport.objects.all()
    serializer_class = SalesReportSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def summary(self, request):
        store_id = request.query_params.get('store_id')
        date_param = request.query_params.get('date')
        period = request.query_params.get('period', 'daily')

        if not store_id or not date_param:
            return Response({'error': '매장 ID와 날짜를 제공해야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return Response({'error': '잘못된 매장 ID입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if period == 'yearly':
                start_date = parse_date(f"{date_param}-01-01")
                end_date = parse_date(f"{date_param}-12-31")
            elif period == 'monthly':
                year, month = date_param.split('-')
                start_date = parse_date(f"{year}-{month}-01")
                end_date = parse_date(f"{year}-{month}-{calendar.monthrange(int(year), int(month))[1]}")
            else:  # daily
                start_date = end_date = parse_date(date_param)
        except ValueError:
            return Response({'error': '잘못된 날짜 형식입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        reports = SalesReport.objects.filter(store=store, date__range=[start_date, end_date])

        if period == 'yearly':
            reports = reports.annotate(period=TruncMonth('date'))
        elif period == 'monthly':
            reports = reports.annotate(period=TruncDay('date'))
        else:  # daily
            reports = reports.values('date').annotate(period=F('date'))

        reports = reports.values('period').annotate(
            total_revenue=Sum('total_revenue'),
            total_expenses=Sum('total_expenses'),
            net_profit=Sum('net_profit')
        ).order_by('period')

        return Response(list(reports))

# 카테고리 뷰셋 정의
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
