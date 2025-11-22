from django.db import models
from django.db.models import F
from django.db.models.functions import Lower
from .company import Company


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

