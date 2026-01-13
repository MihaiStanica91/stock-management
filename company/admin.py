from django.contrib import admin
from .models import Company, Supplier, Product
# Register your models here.

admin.site.register(Company)
admin.site.register(Supplier)
admin.site.register(Product)