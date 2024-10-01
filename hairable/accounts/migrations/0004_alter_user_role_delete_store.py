# Generated by Django 4.2 on 2024-10-01 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_user_role_store'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('CEO', '대표'), ('user', '일반회원')], max_length=50),
        ),
        migrations.DeleteModel(
            name='Store',
        ),
    ]
