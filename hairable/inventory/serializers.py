from rest_framework import serializers
from .models import Category, InventoryItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class InventoryItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = InventoryItem
        fields = ['id', 'category', 'category_name', 'name', 'image', 'purchase_price', 'selling_price', 
                  'usage', 'stock', 'safety_stock', 'stock_value', 'storage_location', 
                  'usage_instructions', 'precautions']

    def validate_category(self, value):
        if not Category.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("지정된 카테고리가 존재하지 않습니다.")
        return value