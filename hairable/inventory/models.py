from django.db import models
from django.core.validators import MinValueValidator  

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='카테고리명')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '카테고리'
        verbose_name_plural = '카테고리들'

class InventoryItem(models.Model):
    USAGE_CHOICES = [
        ('SALE', '매장 판매'),
        ('SERVICE', '매장 시술'),
        ('STAFF', '직원'),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items', verbose_name='카테고리')
    name = models.CharField(max_length=200, verbose_name='제품명')
    image = models.ImageField(upload_to='inventory/', null=True, blank=True, verbose_name='제품 사진')
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='입고가')
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='매장 판매가')
    usage = models.CharField(max_length=10, choices=USAGE_CHOICES, verbose_name='판매 용도')
    stock = models.IntegerField(default=0, verbose_name='재고')
    safety_stock = models.IntegerField(default=0, verbose_name='안전재고')
    storage_location = models.CharField(max_length=100, verbose_name='보관 장소')
    usage_instructions = models.TextField(blank=True, verbose_name='사용 방법')
    precautions = models.TextField(blank=True, verbose_name='사용 주의사항')

    @property
    def stock_value(self):
        # 재고 금액을 계산하여 반환
        return self.purchase_price * self.stock

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # stock_value를 설정하지 않습니다.
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '재고 아이템'
        verbose_name_plural = '재고 아이템들'
