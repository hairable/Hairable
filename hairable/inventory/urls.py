from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


app_name = 'inventory'

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'items', views.InventoryItemViewSet)  # 주석: 'inventory'를 'items'로 변경하여 더 명확하게 함

urlpatterns = [
    path('', include(router.urls)),
]

