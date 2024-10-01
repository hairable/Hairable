from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Store, StoreStaff
from .serializers import StoreSerializer, StoreStaffSerializer
from accounts.permissions import IsCEO

class StoreCreateView(generics.CreateAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated, IsCEO]

    def perform_create(self, serializer):
        # 로그인한 사용자를 ceo로 설정
        serializer.save(ceo=self.request.user)

class StoreListView(generics.ListAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


class StoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


class AddStaffView(generics.CreateAPIView):
    queryset = StoreStaff.objects.all()
    serializer_class = StoreStaffSerializer
    permission_classes = [IsAuthenticated, IsCEO]

    def create(self, request, *args, **kwargs):
        store_id = kwargs.get('store_id')
        store = generics.get_object_or_404(Store, pk=store_id)
        
        user_id = request.data.get('user_id')
        role = request.data.get('role')

        # 직원 추가
        store_staff = StoreStaff(store=store, user_id=user_id, role=role)
        store_staff.save()

        return Response({'message': '직원이 성공적으로 추가되었습니다.'}, status=status.HTTP_201_CREATED)

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