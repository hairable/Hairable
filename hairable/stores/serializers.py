from rest_framework import serializers
from .models import Store, StoreStaff, WorkCalendar
from service.models import Service
from accounts.models import User
from django.shortcuts import get_object_or_404
from django.db import IntegrityError

class StoreStaffSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    available_services = serializers.PrimaryKeyRelatedField(many=True, queryset=Service.objects.all())
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    class Meta:
        model = StoreStaff
        fields = ['user_id', 'store_name', 'user_name', 'role', 'phone', 'date_joined', 'available_services']
        
        
class StoreSerializer(serializers.ModelSerializer):
    ceo_name = serializers.CharField(source='ceo.username', read_only=True)
    staff = StoreStaffSerializer(source='store_staff', many=True, read_only=True)

    class Meta:
        model = Store
        fields = ['id', 'name', 'ceo_name', 'staff']

class WorkCalendarSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = WorkCalendar
        fields = ['id', 'user_id', 'store', 'date', 'start_time', 'end_time', 'status']
        read_only_fields = ['id', 'store']

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        store_id = self.context['view'].kwargs.get('store_id')
        store_staff = StoreStaff.objects.get(store_id=store_id, user_id=user_id)
        
        try:
            work_calendar = WorkCalendar.objects.create(
                staff=store_staff,
                store_id=store_id,
                **validated_data
            )
        except IntegrityError:
            raise serializers.ValidationError("이미 해당 날짜에 스케줄이 존재합니다.")
        
        return work_calendar

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class StaffUpdateSerializer(serializers.ModelSerializer):
    available_services = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), many=True)
    
    class Meta:
        model = StoreStaff
        fields = ['role', 'available_services']

    def update(self, instance, validated_data):
        instance.role = validated_data.get('role', instance.role)
        services = validated_data.get('available_services', [])
        
        # 기존의 제공 가능 서비스 목록을 가져옵니다.
        old_services = set(instance.available_services.all())
        
        # 새로운 제공 가능 서비스로 설정
        instance.available_services.set(services)
        instance.save()

        # 새로운 서비스 목록과 이전 목록을 비교하여 서비스의 디자이너를 업데이트합니다.
        new_services = set(instance.available_services.all())

        # 추가된 서비스에 해당 직원 추가
        added_services = new_services - old_services
        for service in added_services:
            service.available_designers.add(instance)

        # 제거된 서비스에서 해당 직원 제거
        removed_services = old_services - new_services
        for service in removed_services:
            service.available_designers.remove(instance)

        return instance
