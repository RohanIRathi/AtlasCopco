from django import forms

class LoginForm(forms.Form):
    email = forms.CharField(max_length=20)
    password = forms.CharField(max_length=20, widget=forms.PasswordInput)