from django.contrib import admin
from django.urls import path, include
from .ai_assistant import AIAssistantView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls', namespace='accounts')),
    path('api/inventory/', include('inventory.urls', namespace='inventory')),
    path('api/stores/', include('stores.urls', namespace='stores')),
    path('api/service/', include('service.urls')),
    path('api/supplier/', include('supplier.urls')),
    path('ai-assistant/', AIAssistantView.as_view(), name='ai-assistant'),
]
