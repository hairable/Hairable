from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, SupplyViewSet

app_name = 'supplier'  # 주석: URL 네임스페이스 추가

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet)
router.register(r'supplies', SupplyViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
