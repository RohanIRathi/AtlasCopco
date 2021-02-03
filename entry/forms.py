from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from bootstrap_datepicker_plus import DatePickerInput


class NewVisitorForm(ModelForm):
	class Meta:
		model = Visitor
		exclude = ['in_time', 'out_time', 'token', 'qrcode']
		widgets = {
			'expected_in_time': DatePickerInput(),
		}
		# widgets = {
		# 	'in_time': DatePickerInput(
		# 		options={
		# 			'format': 'DD/MM/YYYY hh:mm A',
		# 			'showClear': True,
		# 			'showClose': True,
		# 			'showTodayButton': True,
		# 		}
		# 	),
		# }
