from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from entry.models import *


class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2',]


class CreateEmployeeForm(ModelForm):
	class Meta:
		model = Employee
		fields = ['admin', 'mobile']
		
class PhotoForm(ModelForm):
	class Meta:
		model = Visitor
		fields = ['photo', 'photo_id', 'photo_id_number']