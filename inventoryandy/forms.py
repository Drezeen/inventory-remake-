from django.forms import ModelForm
from django import forms
from .models import Inventoryandy

class AddInventoryForm(ModelForm):
    class Meta:
        model = Inventoryandy
        fields = ['name','cost_per_item','quantity_in_stock','quantity_sold']
        
        

class UpdateInventoryForm(forms.ModelForm):
    barcode = forms.CharField(max_length=100, required=False)  # Add barcode field
    
    class Meta:
        model = Inventoryandy
        fields = ['name', 'cost_per_item', 'quantity_in_stock', 'quantity_sold', 'barcode']