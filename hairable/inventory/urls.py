from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


app_name = 'inventory'

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'items', views.InventoryItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

