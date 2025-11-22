from django.db import models
from .company import Company


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
            The price with VAT included (rounded to 2 decimal places)
        """
        if price is None:
            return None
        vat_amount = price * (self.vat_rate / 100)
        result = price + vat_amount
        # Round to 2 decimal places
        return round(result, 2)
    
    def get_vat_amount(self, price):
        """
        Calculate the VAT amount for a given price.
        
        Args:
            price: The base price (without VAT)
            
        Returns:
            The VAT amount (rounded to 2 decimal places)
        """
        if price is None:
            return None
        result = price * (self.vat_rate / 100)
        # Round to 2 decimal places
        return round(result, 2)
    
    @property
    def display_vat_rate(self):
        """Return VAT rate formatted with % symbol."""
        return f"{self.vat_rate}%"
    
    def __str__(self):
        return f"{self.company.name} - {self.vat_rate}%"

