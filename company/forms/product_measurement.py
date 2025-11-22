from django import forms
from django.forms import ModelForm
from ..models import ProductMeasurement, Company


class TypeOfMeasurementForm(ModelForm):
    class Meta:
        model = ProductMeasurement
        fields = ["type_of_measurement", "company_id"]

    # Remove extra spaces and convert to lowercase
    def clean_type_of_measurement(self):
        value = self.cleaned_data.get('type_of_measurement', '')
        value = ' '.join(value.split()).strip()
        if ProductMeasurement.objects.filter(company_id=self.cleaned_data.get('company_id'), type_of_measurement=value).exists():
            raise forms.ValidationError("Measurement already registered!")
        return value

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['company_id'].queryset = Company.objects.filter(user_id=user)
            self.fields['company_id'].label = "Select Company"
            self.fields['company_id'].required = True

