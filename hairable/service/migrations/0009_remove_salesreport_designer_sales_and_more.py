# Generated by Django 4.2 on 2024-10-20 10:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0008_alter_salesreport_unique_together'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salesreport',
            name='designer_sales',
        ),
        migrations.RemoveField(
            model_name='salesreport',
            name='service_sales',
        ),
    ]
