from django import forms
from django.forms import ModelForm
from ..models import Product, Company, Supplier, ProductCategory, ProductMeasurement, VatRate


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ["company", "supplier", "product_name", "product_category", "product_quantity", "product_measurement", "product_price_without_vat", "product_vat_rate"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['company'].queryset = Company.objects.filter(user_id=user)
            self.fields['company'].label = "Select Company"
            self.fields['company'].required = True
            
            # Get selected company from POST data (if form is bound) or instance (if editing)
            company = None
            if self.is_bound:
                # Form has been submitted - get company from POST data
                company_id = self.data.get('company')
                if company_id:
                    try:
                        company = Company.objects.filter(user_id=user, id=int(company_id)).first()
                    except (ValueError, TypeError):
                        pass
            elif self.instance and self.instance.pk:
                # Editing existing product - use the product's company
                if hasattr(self.instance, 'company') and self.instance.company:
                    company = self.instance.company
            
            # Filter querysets based on selected company
            if company:
                self.fields['supplier'].queryset = Supplier.objects.filter(company_id=company)
                self.fields['product_category'].queryset = ProductCategory.objects.filter(company=company)
                self.fields['product_measurement'].queryset = ProductMeasurement.objects.filter(company_id=company)
                self.fields['product_vat_rate'].queryset = VatRate.objects.filter(company=company)
            else:
                # No company selected - show empty querysets
                self.fields['supplier'].queryset = Supplier.objects.none()
                self.fields['product_category'].queryset = ProductCategory.objects.none()
                self.fields['product_measurement'].queryset = ProductMeasurement.objects.none()
                self.fields['product_vat_rate'].queryset = VatRate.objects.none()
            
            # Set labels and customize display to show only item names
            self.fields['supplier'].label = "Select Supplier"
            self.fields['supplier'].required = True
            self.fields['supplier'].label_from_instance = lambda obj: obj.name
            
            self.fields['product_category'].label = "Select Product Category"
            self.fields['product_category'].required = True
            self.fields['product_category'].label_from_instance = lambda obj: obj.category
            
            self.fields['product_measurement'].label = "Select Product Measurement"
            self.fields['product_measurement'].required = True
            self.fields['product_measurement'].label_from_instance = lambda obj: obj.type_of_measurement
            
            self.fields['product_vat_rate'].label = "Select VAT Rate"
            self.fields['product_vat_rate'].required = True
            self.fields['product_vat_rate'].label_from_instance = lambda obj: f"{obj.vat_rate}%"

    def clean_product_name(self):
        value = self.cleaned_data.get('product_name', '')
        value = ' '.join(value.split()).strip()
        # Allow duplicate product names - product codes are unique per company,
        # so duplicate names with different codes are allowed
        return value

    def clean_product_quantity(self):
        value = self.cleaned_data.get('product_quantity')
        if value is None:
            raise forms.ValidationError("Product quantity is required")
        if value < 0:
            raise forms.ValidationError("Product quantity cannot be negative")
        return value
    
    def clean_product_price_without_vat(self):
        value = self.cleaned_data.get('product_price_without_vat')
        if value is None:
            raise forms.ValidationError("Product price without VAT is required")
        if value < 0:
            raise forms.ValidationError("Product price without VAT cannot be negative")
        return value
    
    def clean_product_vat_rate(self):
        value = self.cleaned_data.get('product_vat_rate')
        if value is None:
            raise forms.ValidationError("VAT rate is required")
        return value
    
    def clean(self):
        cleaned_data = super().clean()
        price_without_vat = cleaned_data.get('product_price_without_vat')
        vat_rate = cleaned_data.get('product_vat_rate')
        
        # Auto-calculate VAT fields if both price and VAT rate are available
        if price_without_vat is not None and vat_rate:
            # Calculate VAT amount
            vat_amount = vat_rate.get_vat_amount(price_without_vat)
            # Calculate total price with VAT
            price_with_vat = vat_rate.calculate_price_with_vat(price_without_vat)
            
            # Set the calculated values
            cleaned_data['product_vat_amount'] = vat_amount
            cleaned_data['product_price_with_vat'] = price_with_vat
        
        return cleaned_data

