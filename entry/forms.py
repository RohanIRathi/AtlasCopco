from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm


class NewVisitorForm(ModelForm):
	class Meta:
		model = Visitor
		exclude = ['in_time', 'out_time', 'token', 'qrcode']
