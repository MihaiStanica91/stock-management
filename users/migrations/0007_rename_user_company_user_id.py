# Generated by Django 4.2.11 on 2024-03-26 17:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_company_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='user',
            new_name='user_id',
        ),
    ]