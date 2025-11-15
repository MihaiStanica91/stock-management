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

class ProductMeasurement(models.Model):
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='quantities')
    type_of_measurement = models.CharField(max_length=200)

    # Each company can't duplicate the same measurement name.
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

class ProductCategory(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='productCategory')
    category = models.CharField(max_length=200)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('category'),
                F('company'),
                name='uniq_company_product_category_ci',
                violation_error_message='Product category with this name already exists in this company!',
            )
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.category}"

class VatRate(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='vatRates')
    vat_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Enter VAT rate as a percentage (e.g., 9.00 for 9%, 23.00 for 23%)"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['vat_rate', 'company'],
                name='uniq_company_vat_rate',
                violation_error_message='Vat rate already registered!',
            )
        ]
    
    def calculate_price_with_vat(self, price):
        """
        Calculate the final price including VAT.
        
        Args:
            price: The base price (without VAT)
            
        Returns:
            The price with VAT included
        """
        if price is None:
            return None
        vat_amount = price * (self.vat_rate / 100)
        return price + vat_amount
    
    def get_vat_amount(self, price):
        """
        Calculate the VAT amount for a given price.
        
        Args:
            price: The base price (without VAT)
            
        Returns:
            The VAT amount
        """
        if price is None:
            return None
        return price * (self.vat_rate / 100)
    
    @property
    def display_vat_rate(self):
        """Return VAT rate formatted with % symbol."""
        return f"{self.vat_rate}%"
    
    def __str__(self):
        return f"{self.company.name} - {self.vat_rate}%"