from django.db import models
from django.db.models import F
from django.db.models.functions import Lower
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
    email = models.EmailField(max_length=100)
    phone_number = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    supplier_code = models.PositiveIntegerField(unique=True, editable=False)
    created_date = models.DateField(auto_now_add=True)
    supplier_details = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['company_id', 'name'],
                name='uniq_company_supplier_name',
                violation_error_message='Supplier with this name already exists in this company!',
            ),
            models.UniqueConstraint(
                fields=['company_id', 'email'],
                name='uniq_company_supplier_email',
                violation_error_message='Supplier with this email already exists in this company!',
            )
        ]

    def save(self, *args, **kwargs):
        if not self.supplier_code:
            last_supplier = Supplier.objects.order_by('-supplier_code').first()
            self.supplier_code = last_supplier.supplier_code + 1 if last_supplier else 100
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.supplier_code} - {self.name}"

class Quantity(models.Model):
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='quantities')
    type_of_measurement = models.CharField(max_length=200)

    # Each company can’t duplicate the same measurement name.
    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('type_of_measurement'),
                F('company_id'),
                name='uniq_company_measurement_ci',
                violation_error_message='Measurement already registered!',
            )
        ]
    def __str__(self):
        return f"{self.company_id.name} - {self.type_of_measurement}"