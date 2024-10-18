from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'stores'

router = DefaultRouter()
router.register(r'stores', views.StoreViewSet, basename='store')
router.register(r'stores/(?P<store_id>\d+)/staff', views.StoreStaffViewSet, basename='store-staff')
router.register(r'stores/(?P<store_id>\d+)/work-calendar', views.WorkCalendarViewSet, basename='work-calendar')
router.register(r'stores/management-calendar', views.ManagementCalendarViewSet, basename='management-calendar')

urlpatterns = [
    path('', include(router.urls)),
]
