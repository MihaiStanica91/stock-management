from django.contrib import admin
from .models import Company, CustomUser, Supplier

# Register your models here.

admin.site.register(Company)
admin.site.register(CustomUser)
admin.site.register(Supplier)