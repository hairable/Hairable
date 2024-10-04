from django.urls import path
from . import views

app_name = 'stores'
urlpatterns = [
    path('create/', views.StoreCreateView.as_view(), name='create_store'),
    path('', views.StoreListView.as_view(), name='list_stores'),
    path('<int:pk>/', views.StoreDetailView.as_view(), name='detail_store'),
    path('<int:store_id>/add-staff/', views.AddStaffView.as_view(), name='add_staff'),
    path('<int:store_id>/remove-staff/<int:user_id>/', views.RemoveStaffView.as_view(), name='remove_staff'),
    path('staff/', views.StoreStaffListView.as_view(), name='store-staff-list'),
    path('work-calendar/create/', views.WorkCalendarCreateView.as_view(), name='work-calendar-create'),
    path('management-calendar/<int:store_id>/', views.ManagementCalendarListView.as_view(), name='management-calendar-list'),
    path('management-calendar/update/<int:store_id>/<str:date>/', views.UpdateManagementCalendarView.as_view(), name='management-calendar-update'),
]
