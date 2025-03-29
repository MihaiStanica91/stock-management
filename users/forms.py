from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth.models import User

from django import forms
from django.forms import ModelForm
from django.forms.widgets import PasswordInput, TextInput
from users.models import Company, CustomUser, Supplier


# - Create/Register a user

class SignUpForm(UserCreationForm):

    class Meta:
        
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


# - Authenticate a user

class LoginForm(AuthenticationForm):

    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())

# - Company registration form
    
class CompanyForm(ModelForm):
    class Meta:

        model = Company
        fields = ["name", "address", "email", "phone_number", "category"]

class SupplierForm(ModelForm):
    class Meta:

        model = Supplier
        fields = ["name", "address", "email", "phone_number"]


class CustomUser(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('role',)
        widgets = {
            'role': forms.HiddenInput(),  # Hide the role field
        }


class EmailForm(forms.Form):
    email = forms.EmailField(label='Email')


class UserEditForm(UserChangeForm):
    password = forms.CharField(label='New Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'readonly': 'readonly'}),
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            user = self.instance
            if user.check_password(password):
                raise forms.ValidationError("Please choose a different password")
        return password
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise forms.ValidationError("First name is required")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise forms.ValidationError("Last name is required")
        return last_name
    

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