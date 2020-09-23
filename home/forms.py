from django import forms
from django.contrib.auth.forms import UserCreationForm
from entry.models import User


class LoginForm(forms.Form):
    email = forms.CharField(max_length=20)
    password = forms.CharField(max_length=20, widget=forms.PasswordInput)


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'mobile']
