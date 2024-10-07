from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceCategoryViewSet, ServiceViewSet

app_name = 'service'  # 주석: URL 네임스페이스 추가

router = DefaultRouter()
router.register(r'categories', ServiceCategoryViewSet)  # 주석: URL 패턴 간소화
router.register(r'services', ServiceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
