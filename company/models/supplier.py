from django.db import models
from .company import Company


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

