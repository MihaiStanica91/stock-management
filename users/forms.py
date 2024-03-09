from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from django import forms

from django.forms.widgets import PasswordInput, TextInput


# - Create/Register a user

class SignUpForm(UserCreationForm):

    class Meta:
        
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


# - Authenticate a user

class LoginForm(AuthenticationForm):

    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())