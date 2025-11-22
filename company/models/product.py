from django.db import models
from .company import Company
from .supplier import Supplier
from .product_category import ProductCategory
from .product_measurement import ProductMeasurement
from .vat_rate import VatRate


class Product(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='products')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products')
    product_code = models.PositiveIntegerField(editable=False)
    product_name = models.CharField(max_length=200)
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    product_measurement = models.ForeignKey(ProductMeasurement, on_delete=models.CASCADE, related_name='products')
    product_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    product_price_without_vat = models.DecimalField(max_digits=10, decimal_places=2)
    product_vat_rate = models.ForeignKey(VatRate, on_delete=models.CASCADE, related_name='products')
    product_price_with_vat = models.DecimalField(max_digits=10, decimal_places=2)
    product_vat_amount = models.DecimalField(max_digits=10, decimal_places=2)
    product_created_date = models.DateField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'product_code'],
                name='uniq_company_product_code',
                violation_error_message='Product code already exists in this company!',
            )
        ]

    def save(self, *args, **kwargs):
        # Set company from supplier (supplier must always have a company)
        if self.supplier_id:
            self.company = self.supplier.company_id
        
        # Auto-increment product code per company starting from 100
        if not self.product_code:
            last_product = Product.objects.filter(company=self.company).order_by('-product_code').first()
            self.product_code = last_product.product_code + 1 if last_product else 100
        
        # Auto-calculate VAT fields if price without VAT and VAT rate are available
        if self.product_price_without_vat and self.product_vat_rate:
            # Calculate VAT amount
            self.product_vat_amount = self.product_vat_rate.get_vat_amount(self.product_price_without_vat)
            # Calculate price with VAT
            self.product_price_with_vat = self.product_vat_rate.calculate_price_with_vat(self.product_price_without_vat)
        
        super().save(*args, **kwargs)

