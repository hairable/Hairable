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
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # 유지
    available_designers = serializers.ListField(write_only=True)  # 추가
    required_inventory = serializers.ListField(write_only=True)   # 추가

    class Meta:
        model = Service
        fields = ['category', 'name', 'price', 'duration', 'available_designers', 'required_inventory']

    def create(self, validated_data):
        available_designers = validated_data.pop('available_designers', [])
        required_inventory = validated_data.pop('required_inventory', [])

        # Service 생성
        service = Service.objects.create(**validated_data)

        # ServiceDesigner 생성
        for designer_data in available_designers:
            store_id = designer_data['store']
            designer_id = designer_data['designer']
            designer = StoreStaff.objects.get(id=designer_id)
            store = Store.objects.get(id=store_id)
            ServiceDesigner.objects.create(service=service, designer=designer, store=store)

        # ServiceInventory 생성
        for inventory_data in required_inventory:
            inventory_item_id = inventory_data['inventory_item']
            quantity = inventory_data['quantity']
            inventory_item = InventoryItem.objects.get(id=inventory_item_id)  # Use InventoryItem here
            ServiceInventory.objects.create(service=service, inventory_item=inventory_item, quantity=quantity)


        return service



    def update(self, instance, validated_data):
        partial = self.context['request'].method == 'PATCH'

        # Update basic fields
        for field in ['category', 'name', 'price', 'duration']:
            if partial and field not in validated_data:
                continue
            setattr(instance, field, validated_data.get(field, getattr(instance, field)))
        instance.save()

        # Update ServiceInventory only if it's provided in partial update
        if 'serviceinventory_set' in validated_data:
            instance.serviceinventory_set.all().delete()
            for inventory_data in validated_data.get('serviceinventory_set', []):
                ServiceInventory.objects.create(service=instance, **inventory_data)

        # Update ServiceDesigner only if it's provided in partial update
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
    customer_gender = serializers.ChoiceField(choices=[('남', '남'), ('여', '여')])
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())
    assigned_designer = serializers.PrimaryKeyRelatedField(queryset=StoreStaff.objects.filter(role='디자이너'), allow_null=True, required=False)
    status = serializers.ChoiceField(choices=[('예약 중', '예약 중'), ('예약 대기', '예약 대기'), ('방문 완료', '방문 완료')], default='예약 대기')
    calculate_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Reservation
        fields = '__all__'
        read_only_fields = ['calculate_cost', 'created_at']

    def create(self, validated_data):
        # 고객 정보 저장
        customer_name = validated_data.pop('customer_name')
        customer_phone_number = validated_data.pop('customer_phone_number')
        customer_gender = validated_data.pop('customer_gender')

        customer, created = Customer.objects.get_or_create(
            name=customer_name,
            phone_number=customer_phone_number,
            defaults={'gender': customer_gender}
        )

        # Increment the reservation count for the customer
        customer.reservation_count += 1
        customer.save()

        # 예약 등록
        validated_data['customer'] = customer
        return super().create(validated_data)

    def validate(self, attrs):
        service = attrs.get('service')
        reservation_time = attrs.get('reservation_time')
        assigned_designer = attrs.get('assigned_designer')

        # Check if the assigned designer is available
        if assigned_designer and Reservation.objects.filter(assigned_designer=assigned_designer, reservation_time=reservation_time).exists():
            raise serializers.ValidationError("The assigned designer is not available at the selected time.")

        # Check if the required inventory is available
        for inventory in service.serviceinventory_set.all():
            if not inventory.inventory_item.is_in_stock(inventory.quantity):
                raise serializers.ValidationError(f"The inventory item '{inventory.inventory_item.name}' is not available in the required quantity.")

        return attrs


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