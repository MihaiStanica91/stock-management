from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, unique = True)
    address = models.CharField(max_length=200)
    email = models.EmailField(max_length = 100, unique = True)
    phone_number = models.CharField(max_length = 100)
    category = models.CharField(max_length=200)
    created_date = models.DateField(auto_now_add = True)

    def __str__(self):
        return self.name

class Supplier(models.Model):
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='suppliers')
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    supplier_code = models.PositiveIntegerField(unique=True, editable=False)
    created_date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.supplier_code:
            last_supplier = Supplier.objects.order_by('-supplier_code').first()
            self.supplier_code = last_supplier.supplier_code + 1 if last_supplier else 100
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.supplier_code} - {self.name}"
