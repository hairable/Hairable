from django.db import models

# Create your models here.

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='카테고리명')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '서비스 카테고리'
        verbose_name_plural = '서비스 카테고리들'

class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services', verbose_name='카테고리')
    name = models.CharField(max_length=100, verbose_name='서비스명')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='기본 단가')

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    class Meta:
        verbose_name = '서비스'
        verbose_name_plural = '서비스들'
