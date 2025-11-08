from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth.models import User
from django import forms
from django.forms.widgets import PasswordInput, TextInput
from .models import CustomUser


# - Create/Register a user

class SignUpForm(UserCreationForm):

    class Meta:
        
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


# - Authenticate a user

class LoginForm(AuthenticationForm):

    username = forms.CharField(widget=TextInput(attrs={'class': 'form-control', 'id': 'floatingInput', 'placeholder': 'Username'}))
    password = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control', 'id': 'floatingPassword', 'placeholder': 'Password'}))


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