from django.contrib import admin
from .models import Category, InventoryItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'stock', 'safety_stock', 'stock_value')
    list_filter = ('category', 'usage')
    search_fields = ('name', 'category__name')
    readonly_fields = ('stock_value',)
