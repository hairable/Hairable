# Generated by Django 4.2 on 2024-10-18 06:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0002_alter_workcalendar_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workcalendar',
            name='staff',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_calendar', to='stores.storestaff'),
        ),
    ]
