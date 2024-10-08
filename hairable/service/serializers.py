from rest_framework import serializers
from .models import Service, Reservation, Customer, SalesReport, ServiceDesigner, ServiceInventory
from stores.models import Category, StoreStaff, Store
from stores.serializers import StoreStaffSerializer
from inventory.models import InventoryItem


class ServiceInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceInventory
        fields = ['inventory_item', 'quantity']
        
class ServiceDesignerSerializer(serializers.ModelSerializer):
    designer = serializers.PrimaryKeyRelatedField(queryset=StoreStaff.objects.all())

    class Meta:
        model = ServiceDesigner
        fields = ['store', 'designer']

class ServiceSerializer(serializers.ModelSerializer):
    available_designers = serializers.PrimaryKeyRelatedField(
        queryset=StoreStaff.objects.all(), many=True, required=False)
    required_inventory = serializers.ListField(
        child=serializers.DictField(), required=False)

    class Meta:
        model = Service
        fields = ['id', 'category', 'name', 'price', 'duration', 'store', 'available_designers', 'required_inventory']

    def create(self, validated_data):
        available_designers = validated_data.pop('available_designers', [])
        required_inventory = validated_data.pop('required_inventory', [])

        service = Service.objects.create(**validated_data)

        # available_designers 저장
        if available_designers:
            service.available_designers.set(available_designers)

        # required_inventory 저장
        for inventory_data in required_inventory:
            inventory_item_id = inventory_data.get('inventory_item')
            quantity = inventory_data.get('quantity')
            inventory_item = InventoryItem.objects.get(id=inventory_item_id)
            ServiceInventory.objects.create(service=service, inventory_item=inventory_item, quantity=quantity)

        return service



    def update(self, instance, validated_data):
        partial = self.context['request'].method == 'PATCH'

        for field in ['category', 'name', 'price', 'duration']:
            if partial and field not in validated_data:
                continue
            setattr(instance, field, validated_data.get(field, getattr(instance, field)))
        instance.save()

        if 'serviceinventory_set' in validated_data:
            instance.serviceinventory_set.all().delete()
            for inventory_data in validated_data.get('serviceinventory_set', []):
                ServiceInventory.objects.create(service=instance, **inventory_data)

        if 'available_designers' in validated_data:
            instance.servicedesigner_set.all().delete()
            for designer_data in validated_data.get('available_designers', []):
                user_id = designer_data['designer']
                designer = StoreStaff.objects.get(user__pk=user_id)
                ServiceDesigner.objects.create(service=instance, designer=designer, store=designer.store)

        return instance

    
class ReservationSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(max_length=100)
    customer_phone_number = serializers.CharField(max_length=15)
    customer_gender = serializers.ChoiceField(choices=[('M', '남'), ('F', '여')])
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())
    assigned_designer = serializers.PrimaryKeyRelatedField(
        queryset=StoreStaff.objects.all(),  # 나중에 유효성 검사에서 필터링할 예정
        allow_null=True, required=False
    )
    status = serializers.ChoiceField(choices=[('예약 중', '예약 중'), ('예약 대기', '예약 대기'), ('방문 완료', '방문 완료')], default='예약 대기')

    class Meta:
        model = Reservation
        fields = '__all__'
        read_only_fields = ['created_at']
        extra_kwargs = {
            'customer': {'required': False}
        }

    def validate(self, attrs):
        # 서비스와 디자이너가 같은 매장에 속하는지 확인
        service = attrs.get('service')
        assigned_designer = attrs.get('assigned_designer')

        if assigned_designer:
            if assigned_designer.store != service.store:
                raise serializers.ValidationError("The assigned designer must be from the same store as the service.")

        return attrs
    
    def create(self, validated_data):
        customer_name = validated_data.pop('customer_name', None)
        customer_phone_number = validated_data.pop('customer_phone_number', None)
        customer_gender = validated_data.pop('customer_gender', None)

        # 고객 정보 저장
        customer, created = Customer.objects.get_or_create(
            name=customer_name,
            phone_number=customer_phone_number,
            defaults={'gender': customer_gender}
        )

        # 예약 생성
        validated_data['customer'] = customer
        validated_data['customer_name'] = customer_name
        validated_data['customer_phone_number'] = customer_phone_number
        validated_data['customer_gender'] = customer_gender

        return super().create(validated_data)




class CustomerSerializer(serializers.ModelSerializer):
    reservations = ReservationSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ['reservation_count']

class SalesReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesReport
        fields = '__all__'
        

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'