from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from entry.models import *


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2','is_superuser' ]



class PhotoForm(ModelForm):
    class Meta:
        model = Visitor
        fields = ['photo', 'photo_id', 'photo_id_number']


class VisitorTokenForm(ModelForm):
    class Meta:
        model = Visitor
        fields = ['visit_token']
