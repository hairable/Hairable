from rest_framework import serializers
from .models import Service, Reservation, Customer, Category, Store, StoreStaff, SalesReport, ServiceDesigner, ServiceInventory
from accounts.models import User
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
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    store = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all())
    available_designers = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False, source='available_designers.user'
    )
    required_inventory = ServiceInventorySerializer(many=True, required=False, source='serviceinventory_set')

    class Meta:
        model = Service
        fields = '__all__'

    def create(self, validated_data):
        available_designers = validated_data.pop('available_designers', [])
        required_inventory = validated_data.pop('serviceinventory_set', [])

        service = Service.objects.create(**validated_data)

        # available_designers 저장
        if available_designers:
            designers = StoreStaff.objects.filter(user__in=available_designers, store=service.store)
            service.available_designers.set(designers)

        # required_inventory 저장
        for inventory_data in required_inventory:
            inventory_item = inventory_data['inventory_item']
            quantity = inventory_data['quantity']
            ServiceInventory.objects.create(service=service, inventory_item=inventory_item, quantity=quantity)

        return service

    def update(self, instance, validated_data):
        available_designers = validated_data.pop('available_designers', None)
        required_inventory = validated_data.pop('serviceinventory_set', None)
        instance = super().update(instance, validated_data)

        # available_designers 업데이트
        if available_designers is not None:
            designers = StoreStaff.objects.filter(user__in=available_designers, store=instance.store)
            instance.available_designers.set(designers)

        # required_inventory 업데이트
        if required_inventory is not None:
            instance.serviceinventory_set.all().delete()
            for inventory_data in required_inventory:
                inventory_item = inventory_data['inventory_item']
                quantity = inventory_data['quantity']
                ServiceInventory.objects.create(service=instance, inventory_item=inventory_item, quantity=quantity)

        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['available_designers'] = [staff.user.id for staff in instance.available_designers.all()]
        return rep


class ReservationSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), required=False)
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())
    assigned_designer = serializers.PrimaryKeyRelatedField(queryset=StoreStaff.objects.all())

    class Meta:
        model = Reservation
        fields = '__all__'

    def validate(self, attrs):
        assigned_designer = attrs.get('assigned_designer')
        service = attrs.get('service')

        # user ID를 기준으로 StoreStaff에서 해당 사용자가 해당 매장에 등록되었는지 확인
        try:
            # assigned_designer는 User 인스턴스이므로, 이를 StoreStaff에서 user_id로 확인
            store_staff = StoreStaff.objects.get(user_id=assigned_designer.id, store=service.store)
        except StoreStaff.DoesNotExist:
            raise serializers.ValidationError("지정된 디자이너는 해당 매장에서 등록되지 않은 상태입니다.")

        # 해당 디자이너가 요청된 서비스를 제공할 수 있는지 확인
        if not store_staff.available_services.filter(id=service.id).exists():
            raise serializers.ValidationError("지정된 디자이너는 선택한 서비스를 제공하지 않습니다.")

        # attrs에 변경된 store_staff를 할당
        attrs['assigned_designer'] = store_staff

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

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['assigned_designer'] = instance.assigned_designer.user.id if instance.assigned_designer else None
        return rep



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
