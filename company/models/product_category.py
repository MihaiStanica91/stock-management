from django.db import models
from django.db.models import F
from django.db.models.functions import Lower
from .company import Company


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

