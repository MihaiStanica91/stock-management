# Generated by Django 4.2.11 on 2024-04-13 11:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_alter_customuser_role'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='adress',
            new_name='address',
        ),
    ]
