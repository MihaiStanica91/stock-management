from django import forms
from django.forms import ModelForm
from ..models import ProductCategory, Company


class ProductCategoryForm(ModelForm):
    class Meta:
        model = ProductCategory
        fields = ["category", "company"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['company'].queryset = Company.objects.filter(user_id=user)
            self.fields['company'].label = "Select Company"
            self.fields['company'].required = True

    def clean_category(self):
        value = self.cleaned_data.get('category', '')
        value = ' '.join(value.split()).strip()
        if ProductCategory.objects.filter(company=self.cleaned_data.get('company'), category=value).exists():
            raise forms.ValidationError("Product category with this name already exists in this company!")
        return value

