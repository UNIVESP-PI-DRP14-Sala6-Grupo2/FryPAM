# Generated by Django 5.1.7 on 2025-03-22 02:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pam', '0006_alter_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tenant',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
