from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls', namespace='accounts')),
    path('api/inventory/', include('inventory.urls', namespace='inventory')),
    path('api/stores/', include('stores.urls', namespace='stores')),
    path('api/', include('service.urls')),
    path('api/', include('supplier.urls')),
]
