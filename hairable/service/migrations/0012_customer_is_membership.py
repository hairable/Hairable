# Generated by Django 4.2 on 2024-10-21 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0011_remove_customer_address_remove_customer_birthday_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='is_membership',
            field=models.BooleanField(default=False),
        ),
    ]