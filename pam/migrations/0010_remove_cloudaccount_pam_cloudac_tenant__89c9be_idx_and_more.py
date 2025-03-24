# Generated by Django 5.1.7 on 2025-03-22 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pam', '0009_alter_cloudaccount_provider'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='cloudaccount',
            name='pam_cloudac_tenant__89c9be_idx',
        ),
        migrations.RenameField(
            model_name='cloudaccount',
            old_name='username',
            new_name='cloud_username',
        ),
        migrations.AlterUniqueTogether(
            name='cloudaccount',
            unique_together={('tenant', 'account', 'provider', 'cloud_username')},
        ),
        migrations.AddIndex(
            model_name='cloudaccount',
            index=models.Index(fields=['tenant', 'account', 'provider', 'cloud_username'], name='pam_cloudac_tenant__75afc1_idx'),
        ),
    ]
