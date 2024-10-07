from django.db import models
from django.core.validators import MinValueValidator  # 주석: 최소값 검증을 위해 추가

# Create your models here.

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='카테고리명')  # 주석: unique=True

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '서비스 카테고리'
        verbose_name_plural = '서비스 카테고리들'

class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services', verbose_name='카테고리')
    name = models.CharField(max_length=100, verbose_name='서비스명')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='기본 단가')  # 주석: 최소값 검증 추가

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    class Meta:
        verbose_name = '서비스'
        verbose_name_plural = '서비스들'
        unique_together = ['category', 'name']  # 주석: 카테고리 내에서 서비스명 중복 방지
