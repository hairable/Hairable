from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet, ReservationViewSet, CustomerViewSet, SalesReportViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'reservations', ReservationViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'sales_reports', SalesReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]