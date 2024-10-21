from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'stores'

router = DefaultRouter()
router.register(r'stores', views.StoreViewSet, basename='store')
router.register(r'stores/(?P<store_id>\d+)/staff', views.StoreStaffViewSet, basename='store-staff')
router.register(r'stores/(?P<store_id>\d+)/work-calendar', views.WorkCalendarViewSet, basename='work-calendar')
urlpatterns = [
    path('', include(router.urls)),
    path('stores/<int:store_id>/work-calendar/monthly-summary/', views.WorkCalendarViewSet.as_view({'get': 'monthly_summary'}), name='work-calendar-monthly-summary'),
    path('stores/<int:store_id>/work-calendar/daily-detail/', views.WorkCalendarViewSet.as_view({'get': 'daily_detail'}), name='work-calendar-daily-detail'),
]