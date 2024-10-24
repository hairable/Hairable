# Generated by Django 4.2 on 2024-10-18 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0004_delete_managementcalendar'),
        ('service', '0005_remove_service_available_designers'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='available_designers',
            field=models.ManyToManyField(related_name='designer_services', to='stores.storestaff'),
        ),
    ]
