# Generated by Django 5.1.7 on 2025-03-22 02:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pam', '0010_remove_cloudaccount_pam_cloudac_tenant__89c9be_idx_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AccountAccessTypes',
            new_name='CloudAccountAccessTypes',
        ),
    ]
