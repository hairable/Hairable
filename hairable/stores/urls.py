from django.urls import path
from .views import StoreCreateView, StoreListView, StoreDetailView, AddStaffView, RemoveStaffView

app_name = 'stores'
urlpatterns = [
    path('create/', StoreCreateView.as_view(), name='create_store'),
    path('', StoreListView.as_view(), name='list_stores'),
    path('<int:pk>/', StoreDetailView.as_view(), name='detail_store'),
    path('<int:store_id>/add-staff/', AddStaffView.as_view(), name='add_staff'),
    path('<int:store_id>/remove-staff/<int:user_id>/', RemoveStaffView.as_view(), name='remove_staff'),
]
