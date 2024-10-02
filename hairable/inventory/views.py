from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, InventoryItem
from .serializers import CategorySerializer, InventoryItemDetailSerializer, InventoryItemUpdateSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemDetailSerializer

    def get_queryset(self):
        queryset = InventoryItem.objects.all()
        category_id = self.request.query_params.get('category_id', None)
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)
        return queryset

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
