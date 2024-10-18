from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Store, StoreStaff, WorkCalendar, ManagementCalendar
from .serializers import StoreSerializer, StoreStaffSerializer, WorkCalendarSerializer, ManagementCalendarSerializer, StaffUpdateSerializer
from accounts.permissions import IsCEO, IsAnyCEO
from django.shortcuts import get_object_or_404
from service.models import Service
from django.contrib.auth import get_user_model
from datetime import datetime
User = get_user_model()




class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated, IsAnyCEO]  # 스토어 생성 권한을 AnyCEO로 설정

    def create(self, request, *args, **kwargs):
        # POST 메서드를 처리하도록 create 메서드를 명시적으로 정의
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_permissions(self):
        # update, partial_update, destroy 시 CEO 권한 필요
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsCEO()]
        return super().get_permissions()

    def perform_create(self, serializer):
        # 스토어 생성 시 현재 사용자(CEO)를 연결
        serializer.save(ceo=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsCEO])
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

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated, IsCEO])
    def remove_staff(self, request, pk=None, staff_pk=None):
        # 직원 삭제 메서드
        store = self.get_object()
        staff = get_object_or_404(StoreStaff, pk=staff_pk, store=store)
        staff.delete()
        return Response({'message': '직원이 성공적으로 삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)
    
class StoreStaffViewSet(viewsets.ModelViewSet):
    queryset = StoreStaff.objects.all()
    serializer_class = StoreStaffSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        store_id = self.kwargs.get('store_id')
        user_id = self.kwargs.get('pk')  # pk 대신 user_id를 사용하여 직원 조회
        return get_object_or_404(StoreStaff, store_id=store_id, user_id=user_id)

    def get_queryset(self):
        store_id = self.kwargs.get('store_id')
        if store_id:
            return StoreStaff.objects.filter(store_id=store_id)
        return super().get_queryset()

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
    
class WorkCalendarViewSet(viewsets.ModelViewSet):
    queryset = WorkCalendar.objects.all()
    serializer_class = WorkCalendarSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def working_staff(self, request):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'detail': '날짜를 입력해주세요 (YYYY-MM-DD 형식).'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({'detail': '날짜 형식이 잘못되었습니다. "YYYY-MM-DD" 형식을 사용하세요.'}, status=status.HTTP_400_BAD_REQUEST)

        working_staff = WorkCalendar.objects.filter(date=date, status='working')
        if not working_staff.exists():
            return Response({'detail': '해당 날짜에 근무 중인 직원이 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(working_staff, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # staff가 존재하는지 확인
        staff_id = request.data.get('staff')
        try:
            staff = User.objects.get(id=staff_id)
        except User.DoesNotExist:
            return Response({'detail': '해당하는 직원이 존재하지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        # serializer에 staff 추가
        serializer.save(staff=staff)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()


class ManagementCalendarViewSet(viewsets.ModelViewSet):
    queryset = ManagementCalendar.objects.all()
    serializer_class = ManagementCalendarSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        store_id = self.kwargs.get('store_id')
        date = self.kwargs.get('date')

        work_calendar = WorkCalendar.objects.filter(store_id=store_id, date=date)
        total_working = work_calendar.filter(status='working').count()
        total_off = work_calendar.filter(status='off').count()

        serializer.save(total_working=total_working, total_off=total_off)

