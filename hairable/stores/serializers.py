from rest_framework import serializers
from .models import Store, StoreStaff, WorkCalendar, ManagementCalendar


class StoreStaffSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = StoreStaff
        fields = ['id', 'store_name', 'user_name', 'role', 'phone', 'date_joined']
        
        
class StoreSerializer(serializers.ModelSerializer):
    ceo_name = serializers.CharField(source='ceo.username', read_only=True)
    staff = StoreStaffSerializer(source='store_staff', many=True, read_only=True)  # store_staff 역참조 사용

    class Meta:
        model = Store
        fields = ['id', 'name', 'ceo_name', 'staff']


class WorkCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkCalendar
        fields = ['staff_id', 'store_id', 'date', 'start_time', 'end_time', 'status']

    def create(self, validated_data):
        # WorkCalendar 생성 시 ManagementCalendar 업데이트
        work_calendar = WorkCalendar.objects.create(**validated_data)

        # ManagementCalendar 업데이트
        management_calendar, created = ManagementCalendar.objects.get_or_create(store=work_calendar.store, date=work_calendar.date)
        management_calendar.update_calendar()

        return work_calendar

    def update(self, instance, validated_data):
        # WorkCalendar 업데이트 시 ManagementCalendar 업데이트
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        # ManagementCalendar 업데이트
        management_calendar, created = ManagementCalendar.objects.get_or_create(store=instance.store, date=instance.date)
        management_calendar.update_calendar()

        return instance

class ManagementCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagementCalendar
        fields = ['store', 'date', 'total_working', 'total_off', 'total_substitute']