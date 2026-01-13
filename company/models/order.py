from django.db import models, transaction
from company.models import Company, Supplier, Product, ProductMeasurement
from django.contrib.auth.models import User


class Order(models.Model):
    order_id = models.ForeignKey(Company, on_delete=models.CASCADE)
    order_number = models.PositiveIntegerField(unique=True, editable=False)
    supplier_id = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    order_notes = models.TextField(blank=True, null=True)
    order_created_date = models.DateField(auto_now_add=True)
    order_created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')

    def __str__(self):
        return f"{self.order_number} - {self.order_id.name}"

    def save(self, *args, **kwargs):
        # Generate an incremental order_number starting at 100 for new records.
        if self._state.adding and self.order_number is None:
            with transaction.atomic():
                last_order = (
                    Order.objects.select_for_update()
                    .order_by('-order_number')
                    .first()
                )
                self.order_number = (last_order.order_number + 1) if last_order else 100
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_order_items')
    supplier_id = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplier_order_items')
    quantity = models.PositiveBigIntegerField(default=1)
    product_measurement_id = models.ForeignKey(ProductMeasurement, on_delete=models.CASCADE, related_name='measurement_order_items')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    order_item_created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.order_number} - {self.product_id.product_name} - {self.supplier_id.name}"