from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/inventory/', include('accounts.urls')),
    path('api/appointments/', include('accounts.urls')),
    path('api/staff/', include('accounts.urls')),
    path('api/sales/', include('accounts.urls')),
    path('api/reports/', include('accounts.urls')),
    path('secretarybot/', include('secretarybot.urls')),
]
