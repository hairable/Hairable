from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Store, StoreStaff, WorkCalendar, ManagementCalendar
from .serializers import StoreSerializer, StoreStaffSerializer, WorkCalendarSerializer, ManagementCalendarSerializer
from accounts.permissions import IsCEO, IsAnyCEO
from django.contrib.auth import get_user_model

User = get_user_model()

class StoreCreateView(generics.CreateAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated, IsAnyCEO]

    def perform_create(self, serializer):
        serializer.save(ceo=self.request.user)

class StoreListView(generics.ListAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


class StoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    # 다른 메서드(GET 등)는 permission_classes 없이 허용
    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [IsAuthenticated(), IsCEO()]
        return []  

    def update(self, request, *args, **kwargs):
        partial = True 
        return super().update(request, *args, partial=partial, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'message': '스토어가 성공적으로 삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)

# 직원 추가
class AddStaffView(generics.CreateAPIView):
    queryset = StoreStaff.objects.all()
    serializer_class = StoreStaffSerializer
    permission_classes = [IsAuthenticated, IsCEO]

    def create(self, request, *args, **kwargs):
        store_id = kwargs.get('store_id')
        store = generics.get_object_or_404(Store, pk=store_id)
        
        user_id = request.data.get('user_id')
        role = request.data.get('role')
        store_staff = StoreStaff(store=store, user_id=user_id, role=role)
        store_staff.save()

        return Response({'message': '직원이 성공적으로 추가되었습니다.'}, status=status.HTTP_201_CREATED)
# 직원 삭제
class RemoveStaffView(generics.DestroyAPIView):
    queryset = StoreStaff.objects.all()
    permission_classes = [IsAuthenticated, IsCEO]

    def delete(self, request, store_id, user_id):
        try:
            staff = StoreStaff.objects.get(store_id=store_id, user_id=user_id)
            staff.delete()
            return Response({'message': '직원이 성공적으로 삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)
        except StoreStaff.DoesNotExist:
            return Response({'message': '해당 직원이 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)

# 매장별 직원 목록 조회 및 검색 기능
class StoreStaffListView(generics.ListAPIView):
    serializer_class = StoreStaffSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        store_id = self.request.query_params.get('store_id')
        if store_id:
            return StoreStaff.objects.filter(store_id=store_id)
        return StoreStaff.objects.all()
    
# 근무 캘린더 생성 및 업데이트
class WorkCalendarCreateView(generics.CreateAPIView):
    queryset = WorkCalendar.objects.all()
    serializer_class = WorkCalendarSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # 요청에서 staff_id와 store_id를 받음
        staff_id = request.data.get('staff_id')
        store_id = request.data.get('store_id')
        date = request.data.get('date')

        # 필수 값이 없을 경우 에러 반환
        if not staff_id:
            return Response({'error': 'staff_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not store_id:
            return Response({'error': 'store_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Store와 Staff(User) 객체 가져오기
        store = generics.get_object_or_404(Store, pk=store_id)
        staff = generics.get_object_or_404(User, pk=staff_id)

        # 근무표에 기존 일정이 있는지 확인
        existing_calendar = WorkCalendar.objects.filter(staff=staff, store=store, date=date).first()

        if existing_calendar:
            # 기존 근무 상태가 있다면 업데이트
            existing_calendar.status = request.data.get('status')
            existing_calendar.start_time = request.data.get('start_time')
            existing_calendar.end_time = request.data.get('end_time')
            existing_calendar.save()
        else:
            # 새 근무표 생성
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(staff=staff, store=store)

        # 관리 캘린더 업데이트
        self.update_management_calendar(store_id, date)

        return Response({'message': '근무 상태가 성공적으로 등록되었습니다.'}, status=status.HTTP_201_CREATED)

    def update_management_calendar(self, store_id, date):
        # 관리 캘린더 업데이트 로직
        work_calendar = WorkCalendar.objects.filter(store_id=store_id, date=date)
        total_working = work_calendar.filter(status='working').count()
        total_off = work_calendar.filter(status='off').count()

        management_calendar, created = ManagementCalendar.objects.get_or_create(store_id=store_id, date=date)
        management_calendar.total_working = total_working
        management_calendar.total_off = total_off
        management_calendar.save()


# 관리 캘린더 목록
class ManagementCalendarListView(generics.ListAPIView):
    serializer_class = ManagementCalendarSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        store_id = self.kwargs.get('store_id')
        if store_id:
            return ManagementCalendar.objects.filter(store__id=store_id)
        return ManagementCalendar.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# 관리 캘린더 업데이트(일단 만들어 놓긴했는데, 삭제해도 될것같음)
class UpdateManagementCalendarView(generics.UpdateAPIView):
    queryset = ManagementCalendar.objects.all()
    serializer_class = ManagementCalendarSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        store_id = self.kwargs.get('store_id')
        date = self.kwargs.get('date')

        # 근무 일정에 따라 관리 캘린더 업데이트
        work_calendar = WorkCalendar.objects.filter(store_id=store_id, date=date)
        total_working = work_calendar.filter(status='working').count()
        total_off = work_calendar.filter(status='off').count()

        serializer.save(total_working=total_working, total_off=total_off)

        return Response({'message': '관리 캘린더가 성공적으로 업데이트되었습니다.'})