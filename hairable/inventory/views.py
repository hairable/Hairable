from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, InventoryItem
from .serializers import CategorySerializer, InventoryItemDetailSerializer, InventoryItemUpdateSerializer
from rest_framework.permissions import IsAuthenticated  # 인증된 사용자만 접근 가능하도록 추가

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemDetailSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        queryset = InventoryItem.objects.all()
        category_id = self.request.query_params.get('category_id', None)
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        category_id = request.data.get('category')
        if not category_id:
            return Response({"error": "Category is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"error": "Invalid category ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save(category=category)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['patch'])
    def update_field(self, request, pk=None):
        item = self.get_object()
        field = request.data.get('field')
        value = request.data.get('value')

        if field not in InventoryItemUpdateSerializer.Meta.fields:
            return Response({"error": "Invalid field"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = InventoryItemUpdateSerializer(item, data={field: value}, partial=True, context={'update_field': field})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
