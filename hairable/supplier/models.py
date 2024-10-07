from django.db import models
from inventory.models import InventoryItem
from django.core.validators import MinValueValidator  # 주석: 최소값 검증을 위해 추가

# Create your models here.

class Supplier(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='공급업체명')  # 주석: unique=True 추가
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
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name='수량')  # 주석: 최소값 검증 추가
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='개별 단가')  # 주석: 최소값 검증 추가
    total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False, verbose_name='총 가격')  # 주석: 총 가격 필드 추가
    supply_date = models.DateField(verbose_name='납품 일자')
    received_date = models.DateField(verbose_name='수령일')
    payment_date = models.DateField(verbose_name='입금 일자', null=True, blank=True)

    def __str__(self):
        return f"{self.supplier.name} - {self.inventory_item.name} ({self.supply_date})"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price  # 주석: 총 가격 계산
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:  # 새로운 Supply 객체인 경우에만 재고를 업데이트
            self.inventory_item.stock += self.quantity
            self.inventory_item.save()
    class Meta:
        verbose_name = '납품'
        verbose_name_plural = '납품들'
