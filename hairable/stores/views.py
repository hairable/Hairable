import logging
from calendar import monthrange
from datetime import datetime
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from dateutil import parser
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from utils.permissions import UserRolePermission
from service.models import Service
from .models import Store, StoreStaff, WorkCalendar
from .serializers import (
    StoreSerializer,
    StoreStaffSerializer,
    WorkCalendarSerializer
)

User = get_user_model()
logger = logging.getLogger(__name__)

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), UserRolePermission("CEO")]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), UserRolePermission("CEO")]
        elif self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), UserRolePermission("CEO", "manager","designer")]

    
    def create(self, request, *args, **kwargs):
        # POST 메서드를 처리하도록 create 메서드를 명시적으로 정의
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def perform_create(self, serializer):
        # 스토어 생성 시 현재 사용자(CEO)를 연결
        serializer.save(ceo=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, UserRolePermission("CEO")])
    def add_staff(self, request, pk=None):
        # 직원 추가 메서드
        store = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role')
        available_services = request.data.get('available_services', [])

        if StoreStaff.objects.filter(store=store, user_id=user_id).exists():
            return Response({'message': '해당 직원은 이미 이 매장에 등록되어 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        store_staff = StoreStaff.objects.create(store=store, user_id=user_id, role=role)
        if available_services:
            services = Service.objects.filter(id__in=available_services)
            store_staff.available_services.set(services)
        store_staff.save()

        return Response({'message': '직원이 성공적으로 추가되었습니다.'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated, UserRolePermission("CEO")])
    def remove_staff(self, request, pk=None, staff_pk=None):
        # 직원 삭제 메서드
        store = self.get_object()
        staff = get_object_or_404(StoreStaff, pk=staff_pk, store=store)
        staff.delete()
        return Response({'message': '직원이 성공적으로 삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            store_id = instance.id
            ceo_id = instance.ceo.id
            self.perform_destroy(instance)
            return Response({
                'message': '스토어가 성공적으로 삭제되었습니다.',
                'store_id': store_id,
                'ceo_id': ceo_id
            }, status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response({'error': '스토어를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class StoreStaffViewSet(viewsets.ModelViewSet):
    queryset = StoreStaff.objects.all()
    serializer_class = StoreStaffSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsAuthenticated(), UserRolePermission("CEO", "manager")]
        elif self.action in ['update', 'partial_update']:
            if 'role' in self.request.data:
                return [IsAuthenticated(), UserRolePermission("CEO")]
            return [IsAuthenticated(), UserRolePermission("CEO", "manager")]
        return [IsAuthenticated(), UserRolePermission("CEO", "manager","designer")]

    def get_object(self):
        store_id = self.kwargs.get('store_id')
        user_id = self.kwargs.get('pk')  # pk 대신 user_id를 사용하여 직원 조회
        return get_object_or_404(StoreStaff, store_id=store_id, user_id=user_id)

    def get_queryset(self):
        store_id = self.kwargs.get('store_id')
        queryset = StoreStaff.objects.filter(store_id=store_id)
        
        query = self.request.query_params.get('query')
        if query:
            queryset = queryset.filter(
                Q(user__username__icontains=query) |
                Q(user__id__icontains=query)
            )
        
        return queryset

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True  # 부분 업데이트 허용
        instance = self.get_object()
        old_services = set(instance.available_services.all())  # 업데이트 전의 서비스 목록

        # 업데이트된 직원 정보 저장
        response = super().update(request, *args, **kwargs)

        # 업데이트 후의 서비스 목록
        new_services = set(instance.available_services.all())

        # 추가된 서비스에 해당 직원 추가
        added_services = new_services - old_services
        for service in added_services:
            service.available_designers.add(instance)

        # 제거된 서비스에서 해당 직원 제거
        removed_services = old_services - new_services
        for service in removed_services:
            service.available_designers.remove(instance)

        return response
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class WorkCalendarViewSet(viewsets.ModelViewSet):
    queryset = WorkCalendar.objects.all()
    serializer_class = WorkCalendarSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            return [IsAuthenticated(), UserRolePermission("CEO", "manager","designer")]
        return [IsAuthenticated(), UserRolePermission("CEO", "manager","designer")]

    def get_queryset(self):
        store_id = self.kwargs.get('store_id')
        return WorkCalendar.objects.filter(store_id=store_id)

    @action(detail=False, methods=['get'], url_path='monthly-summary')
    def monthly_summary(self, request, store_id=None):
        year = request.query_params.get('year')
        month = request.query_params.get('month')

        if not all([store_id, year, month]):
            return Response({'detail': '매장 ID, 년도, 월을 모두 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            year = int(year)
            month = int(month)
            _, last_day = monthrange(year, month)
            start_date = datetime(year, month, 1)
            end_date = datetime(year, month, last_day)
        except ValueError:
            return Response({'detail': '올바른 년도와 월을 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        daily_summary = WorkCalendar.objects.filter(
            store_id=store_id,
            date__range=[start_date, end_date]
        ).values('date').annotate(
            working_count=Count('id', filter=models.Q(status='working')),
            off_count=Count('id', filter=models.Q(status='off'))
        ).order_by('date')

        return Response(daily_summary)

    @action(detail=False, methods=['get'], url_path='daily-detail')
    def daily_detail(self, request, store_id=None):
        date = request.query_params.get('date')

        if not all([store_id, date]):
            return Response({'detail': '매장 ID와 날짜를 모두 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'detail': '올바른 날짜 형식을 입력해주세요 (YYYY-MM-DD).'}, status=status.HTTP_400_BAD_REQUEST)

        daily_detail = WorkCalendar.objects.filter(
            store_id=store_id,
            date=date,
        ).select_related('staff__user', 'store').values(
            'staff__user__id',
            'staff__user__username',
            'start_time',
            'end_time',
            'status',
            'store__name'
        )

        if not daily_detail:
            return Response({'detail': '해당 날짜에 대한 근무 일정이 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        store_name = daily_detail[0]['store__name'] if daily_detail else None

        response_data = {
            'store_name': store_name,
            'date': date,
            'schedules': list(daily_detail)
        }

        return Response(response_data)
    
    def perform_create(self, serializer):
        serializer.save()
        
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

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

        if new_status == '방문 완료' and old_status != '방문 완료':
            try:
                reservation.record_sales()
            except Exception as e:
                logger.error(f"Sales report update failed: {str(e)}")
                return Response({'message': '예약 상태가 변경되었지만, 매출 보고서 업데이트에 실패했습니다.'}, status=status.HTTP_200_OK)

        return Response({'message': '예약이 성공적으로 수정되었습니다.'})