from rest_framework import serializers
from .models import Store, StoreStaff


# 매장 이름 중복 방지
class StoreSerializer(serializers.ModelSerializer):
    ceo_name = serializers.CharField(source='ceo.username', read_only=True)  # CEO의 username을 가져오는 필드

    class Meta:
        model = Store
        fields = ['id', 'name', 'ceo', 'ceo_name', 'staff']  # 필요한 필드만 명시적으로 나열
        extra_kwargs = {
            'ceo': {'required': False}  # ceo 필드를 선택적 필드로 변경
        }

    def validate_name(self, value):
        if Store.objects.filter(name=value).exists():
            raise serializers.ValidationError("이 이름은 이미 사용 중입니다.")
        return value

class StoreStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreStaff
        fields = '__all__'
        
