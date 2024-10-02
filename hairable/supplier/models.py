from django.db import models
from inventory.models import InventoryItem

# Create your models here.

class Supplier(models.Model):
    name = models.CharField(max_length=100, verbose_name='공급업체명')
    contact_person = models.CharField(max_length=100, verbose_name='담당자')
    phone = models.CharField(max_length=20, verbose_name='전화번호')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '공급업체'
        verbose_name_plural = '공급업체들'

class Supply(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplies', verbose_name='공급업체')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='supplies', verbose_name='재고 아이템')
    quantity = models.PositiveIntegerField(verbose_name='수량')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='개별 단가')
    supply_date = models.DateField(verbose_name='납품 일자')
    received_date = models.DateField(verbose_name='수령일')
    payment_date = models.DateField(verbose_name='입금 일자', null=True, blank=True)

    def __str__(self):
        return f"{self.supplier.name} - {self.inventory_item.name} ({self.supply_date})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:  # 새로운 Supply 객체인 경우에만 재고를 업데이트
            self.inventory_item.stock += self.quantity
            self.inventory_item.save()

    class Meta:
        verbose_name = '납품'
        verbose_name_plural = '납품들'
