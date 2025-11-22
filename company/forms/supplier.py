from django import forms
from django.forms import ModelForm
from ..models import Supplier, Company


class SupplierForm(ModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "address", "email", "phone_number", "supplier_details", "company_id"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['company_id'].queryset = Company.objects.filter(user_id=user)
            self.fields['company_id'].label = "Select Company"
            self.fields['company_id'].required = True

    def clean(self):
        cleaned_data = super().clean()
        company_id = cleaned_data.get('company_id')
        if company_id:
            for field_name, error_msg in [('name', 'name'), ('email', 'email')]:
                value = cleaned_data.get(field_name)
                if value and Supplier.objects.filter(company_id=company_id, **{field_name: value}).exclude(pk=self.instance.pk or 0).exists():
                    self.add_error(field_name, f'Supplier with this {error_msg} already exists in this company!')
        return cleaned_data


class SupplierEditForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'address', 'email', 'phone_number', 'supplier_details']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required")
        if self.instance.company_id and Supplier.objects.filter(company_id=self.instance.company_id, email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Supplier with this email already exists in this company!')
        return email

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Name is required")
        if self.instance.company_id and Supplier.objects.filter(company_id=self.instance.company_id, name=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Supplier with this name already exists in this company!')
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

    def clean_details(self):
        supplier_details = self.cleaned_data.get('supplier_details')
        if not supplier_details:
            raise forms.ValidationError("Add some details about this supplier")
        return supplier_details

