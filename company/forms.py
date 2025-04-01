from django import forms
from django.forms import ModelForm
from .models import Company, Supplier

class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ["name", "address", "email", "phone_number", "category"]


class CompanyEditForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'address', 'email', 'phone_number', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].disabled = True  # Make email field read-only

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Name is required")
        return name

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if not address:
            raise forms.ValidationError("Address is required")
        return address

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number:
            raise forms.ValidationError("Phone number is required")
        return phone_number 
    

class SupplierForm(ModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "address", "email", "phone_number", "company_id"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['company_id'].queryset = Company.objects.filter(user_id=user)
            self.fields['company_id'].label = "Select Company"
            self.fields['company_id'].required = True