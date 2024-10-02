from rest_framework import serializers
from .models import ServiceCategory, Service

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class ServiceCategorySerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'services']

class ServiceCreateSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(write_only=True)

    class Meta:
        model = Service
        fields = ['category_name', 'name', 'price']

    def create(self, validated_data):
        category_name = validated_data.pop('category_name')
        category, _ = ServiceCategory.objects.get_or_create(name=category_name)
        service = Service.objects.create(category=category, **validated_data)
        return service
