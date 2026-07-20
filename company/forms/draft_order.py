from django import forms
from company.models import Supplier, Product, ProductMeasurement, Company

class DraftOrderItemForm(forms.Form):
    """Form for adding items to a draft order (before order creation)"""
    company_id = forms.ModelChoiceField(
        queryset=Company.objects.none(),
        label="Select Company",
        required=True
    )
    supplier_id = forms.ModelChoiceField(
        queryset=Supplier.objects.none(),
        label="Select Supplier",
        required=True
    )
    product_id = forms.ModelChoiceField(
        queryset=Product.objects.none(),
        label="Select Product",
        required=True
    )
    quantity = forms.DecimalField(
        label="Quantity",
        required=True,
        min_value=0.01
    )
    product_measurement_id = forms.ModelChoiceField(
        queryset=ProductMeasurement.objects.none(),
        label="Product Measurement",
        required=True
    )
    price = forms.DecimalField(
        label="Price",
        required=True,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter companies by user
            companies = Company.objects.filter(user_id=user.id)
            self.fields['company_id'].queryset = companies
            self.fields['company_id'].label_from_instance = lambda obj: obj.name
            
            # Set label_from_instance for all fields
            self.fields['supplier_id'].label_from_instance = lambda obj: obj.name
            self.fields['product_id'].label_from_instance = lambda obj: obj.product_name
            self.fields['product_measurement_id'].label_from_instance = lambda obj: obj.type_of_measurement
            
            # If form is being submitted (has POST data), allow all valid options for user's companies
            # This ensures validation works even if JavaScript populated the fields
            if self.data:
                # Allow all suppliers, products, and measurements for user's companies
                # We'll validate the company relationship in clean()
                self.fields['supplier_id'].queryset = Supplier.objects.filter(company_id__user_id=user.id)
                self.fields['product_id'].queryset = Product.objects.filter(company__user_id=user.id)
                self.fields['product_measurement_id'].queryset = ProductMeasurement.objects.filter(company_id__user_id=user.id)
            else:
                # Form is being displayed (GET request), keep querysets empty
                # JavaScript will populate them based on company selection
                self.fields['supplier_id'].queryset = Supplier.objects.none()
                self.fields['product_id'].queryset = Product.objects.none()
                self.fields['product_measurement_id'].queryset = ProductMeasurement.objects.none()
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate that selected items belong to the selected company
        company = cleaned_data.get('company_id')
        supplier = cleaned_data.get('supplier_id')
        product = cleaned_data.get('product_id')
        measurement = cleaned_data.get('product_measurement_id')
        
        if company:
            if supplier and supplier.company_id != company:
                self.add_error('supplier_id', 'This supplier does not belong to the selected company.')
            
            if product:
                if product.company != company:
                    self.add_error('product_id', 'This product does not belong to the selected company.')
                # Validate product belongs to selected supplier
                if supplier and product.supplier != supplier:
                    self.add_error('product_id', 'This product does not belong to the selected supplier.')
                # Auto-set price from product if not set
                if not cleaned_data.get('price') and product:
                    cleaned_data['price'] = product.product_price_with_vat
                # Auto-set measurement from product if not set
                if not measurement and product:
                    cleaned_data['product_measurement_id'] = product.product_measurement
            
            if measurement and measurement.company_id != company:
                self.add_error('product_measurement_id', 'This measurement does not belong to the selected company.')
        
        price = cleaned_data.get('price')
        quantity = cleaned_data.get('quantity')
        
        if price is not None and quantity is not None:
            cleaned_data['total'] = price * quantity
        else:
            cleaned_data['total'] = 0
        
        return cleaned_data

class CreateOrderForm(forms.Form):
    """Form for creating order from draft items"""
    order_notes = forms.CharField(
        label="Order Notes",
        required=False,
        widget=forms.Textarea(attrs={'rows': 3})
    )

class SearchOrderForm(forms.Form):
    order_number = forms.CharField(label="Search Order Number", required=False)
    order_supplier = forms.CharField(label="Search Order Supplier", required=False)
    order_product = forms.CharField(label="Search Order Product", required=False)