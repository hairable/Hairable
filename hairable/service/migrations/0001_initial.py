# Generated by Django 4.2 on 2024-10-13 11:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('gender', models.CharField(max_length=10)),
                ('phone_number', models.CharField(max_length=15)),
                ('membership_status', models.CharField(choices=[('일반 고객', '일반 고객'), ('멤버십 가입 고객', '멤버십 가입 고객')], default='일반 고객', max_length=20)),
                ('reservation_count', models.IntegerField(default=0)),
                ('notes', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(blank=True, max_length=255, null=True)),
                ('customer_phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('customer_gender', models.CharField(blank=True, choices=[('M', '남'), ('F', '여')], max_length=1, null=True)),
                ('reservation_time', models.DateTimeField()),
                ('status', models.CharField(choices=[('예약 중', '예약 중'), ('예약 대기', '예약 대기'), ('방문 완료', '방문 완료')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SalesReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('total_revenue', models.DecimalField(decimal_places=2, max_digits=15)),
                ('total_expenses', models.DecimalField(decimal_places=2, max_digits=15)),
                ('net_profit', models.DecimalField(decimal_places=2, max_digits=15)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('duration', models.DurationField()),
            ],
        ),
        migrations.CreateModel(
            name='ServiceDesigner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceInventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('inventory_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.inventoryitem')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service.service')),
            ],
        ),
    ]
