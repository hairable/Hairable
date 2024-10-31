from rest_framework import serializers
from .models import Category, InventoryItem

class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ['id', 'name', 'purchase_price', 'selling_price', 'usage', 'stock', 'safety_stock', 'stock_value', 'storage_location', 'usage_instructions', 'precautions']
        read_only_fields = ['id', 'stock_value']

class CategorySerializer(serializers.ModelSerializer):
    items = InventoryItemSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'items']

class InventoryItemDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = InventoryItem
        fields = ['id', 'category', 'category_name', 'name', 'image', 'purchase_price', 'selling_price', 
                'usage', 'stock', 'safety_stock', 'stock_value', 'storage_location', 
                'usage_instructions', 'precautions']
        read_only_fields = ['id', 'category_name']

class InventoryItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ['id', 'name', 'image', 'purchase_price', 'selling_price', 'usage', 'stock', 'safety_stock', 'stock_value', 'storage_location', 'usage_instructions', 'precautions']
        read_only_fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            for field in self.fields:
                if field != self.context['update_field']:
                    self.fields[field].read_only = True