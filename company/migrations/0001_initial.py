# Generated by Django 4.2.11 on 2025-04-01 16:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('address', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('phone_number', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=200)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('phone_number', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=200)),
                ('supplier_code', models.PositiveIntegerField(editable=False, unique=True)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suppliers', to='company.company')),
            ],
        ),
    ]
