# Generated by Django 4.2 on 2024-10-13 11:01

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='카테고리명')),
            ],
            options={
                'verbose_name': '카테고리',
                'verbose_name_plural': '카테고리들',
            },
        ),
        migrations.CreateModel(
            name='InventoryItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='제품명')),
                ('image', models.ImageField(blank=True, null=True, upload_to='inventory/', verbose_name='제품 사진')),
                ('purchase_price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='입고가')),
                ('selling_price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='매장 판매가')),
                ('usage', models.CharField(choices=[('SALE', '매장 판매'), ('SERVICE', '매장 시술'), ('STAFF', '직원')], max_length=10, verbose_name='판매 용도')),
                ('stock', models.IntegerField(default=0, verbose_name='재고')),
                ('safety_stock', models.IntegerField(default=0, verbose_name='안전재고')),
                ('storage_location', models.CharField(max_length=100, verbose_name='보관 장소')),
                ('usage_instructions', models.TextField(blank=True, verbose_name='사용 방법')),
                ('precautions', models.TextField(blank=True, verbose_name='사용 주의사항')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='inventory.category', verbose_name='카테고리')),
            ],
            options={
                'verbose_name': '재고 아이템',
                'verbose_name_plural': '재고 아이템들',
            },
        ),
    ]
