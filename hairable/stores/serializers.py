from rest_framework import serializers
from .models import Store, StoreStaff

class StoreSerializer(serializers.ModelSerializer):
    ceo_name = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = ['id', 'name', 'ceo_name', 'staff']  

    def get_ceo_name(self, obj):
        return obj.ceo.username if obj.ceo else None 

# 매장 이름 중복 방지
class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'
        extra_kwargs = {
            'ceo': {'required': False}  # ceo 필드를 선택적 필드로 변경
        }

    def validate_name(self, value):
        if Store.objects.filter(name=value).exists():
            raise serializers.ValidationError("이 이름은 이미 사용 중입니다.")
        return value

    def get_ceo_name(self, obj):
        return obj.ceo.username  # CEO의 username을 반환합니다.

class StoreStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreStaff
        fields = '__all__'
        
