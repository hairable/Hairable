from rest_framework import serializers
from .models import Supplier, Supply
from inventory.models import InventoryItem

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class SupplySerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    inventory_item_name = serializers.CharField(source='inventory_item.name', read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Supply
        fields = ['id', 'supplier', 'supplier_name', 'inventory_item', 'inventory_item_name', 'quantity', 'unit_price', 'total_price', 'supply_date', 'received_date', 'payment_date']

class SupplyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supply
        fields = ['supplier', 'inventory_item', 'quantity', 'unit_price', 'supply_date', 'received_date', 'payment_date']

    def create(self, validated_data):
        supply = Supply.objects.create(**validated_data)
        # 총 가격 계산
        supply.total_price = supply.quantity * supply.unit_price
        supply.save()
        return supply

    def validate_inventory_item(self, value):
        if not InventoryItem.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("지정된 재고 아이템이 존재하지 않습니다.")
        return value
