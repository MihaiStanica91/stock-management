from django import forms
from django.forms import ModelForm
from ..models import VatRate, Company


class VatRateForm(ModelForm):
    class Meta:
        model = VatRate
        fields = ["vat_rate", "company"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['company'].queryset = Company.objects.filter(user_id=user)
            self.fields['company'].label = "Select Company"
            self.fields['company'].required = True

    def clean_vat_rate(self):
        value = self.cleaned_data.get('vat_rate')
        if value is None:
            raise forms.ValidationError("VAT rate is required")
        if value < 0:
            raise forms.ValidationError("VAT rate cannot be negative")
        if value > 100:
            raise forms.ValidationError("VAT rate cannot exceed 100%")
        return value

    def clean(self):
        cleaned_data = super().clean()
        vat_rate = cleaned_data.get('vat_rate')
        company = cleaned_data.get('company')
        
        # Check for duplicate VAT rate in the same company
        if vat_rate is not None and company:
            if VatRate.objects.filter(company=company, vat_rate=vat_rate).exclude(pk=self.instance.pk or 0).exists():
                error_message = "VAT rate already registered for this company!"
                # Add error to both fields so Bootstrap shows red X on both
                self.add_error('vat_rate', error_message)
                self.add_error('company', error_message)
        
        return cleaned_data

