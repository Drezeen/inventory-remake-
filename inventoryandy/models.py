from django.db import models

class Inventoryandy(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    cost_per_item = models.DecimalField(max_digits=19, decimal_places=2, null=False, blank=False)
    quantity_in_stock =models.IntegerField(null=False, blank=False)
    quantity_sold = models.IntegerField(null=False, blank=False)
    remaining_quantity = models.IntegerField(null=False, blank=False)
    sales = models.DecimalField(max_digits=19, decimal_places=2, null=False, blank=False)
    stock_date = models.DateField(auto_now_add=True)
    last_sales_date = models.DateField(auto_now = True)
    barcode = models.CharField(max_length=50, unique=True)
    
    def __str__(self) -> str:
        return self.name
    
