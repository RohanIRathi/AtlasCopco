from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls.base import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView
from django.urls import reverse
from django.core.mail import EmailMessage
from django.conf import settings

import os
from datetime import datetime
from PIL import Image
from .forms import *
from io import BytesIO
import base64
import pyzbar.pyzbar as pb
from home import views as hviews

def is_security(user):
	try:
		admin = not User.objects.get(username=user).is_superuser and User.objects.get(username=user).is_staff
		return admin
	except:
		return False

# Create your views here.
@login_required
def new_visitor(request):
	if not hviews.is_security(request.user):
		employees = User.objects.all()
		form = NewVisitorForm()
		if request.method == 'POST':
			form = NewVisitorForm(request.POST, request.FILES)
			if form.is_valid():
				visitor = form.save(commit=False)
				visitor.save()
				qrcodeimg, visitor.token = generateQR(visitor.id, 'booking')
				send_qrcode_email(visitor.email, qrcodeimg) # email to send the qr code to the visitor
				os.remove(qrcodeimg)
				visitor.save()
				messages.success(request, 'QR Code has been sent to the visitor\'s email-id')
				return redirect('/')
			else:
				print(form.errors)
				messages.error(request, 'Error!')
		context = {'form': form, 'employees': employees}
		return render(request, 'entry/visitor_booking.html', context)
	else:
		return redirect('/')


def generateQR(id, qrtype):
	import qrcode
	display_visitors = Visitor.objects.filter(session_expired=False)
	qr = qrcode.QRCode(
		version=1,
		error_correction=qrcode.constants.ERROR_CORRECT_L,
		box_size=5,
		border=4
	)
	if qrtype == 'booking':
		visitor = display_visitors.get(id=id)  # visitors id
		token = str(visitor.name).upper() + ' ' + str(visitor.id) + ' (V)'
		qr.add_data(token)
		qr.make(fit=True)
		img = qr.make_image(fill_color="black", back_color="white")
		qrpath = "./media/qrcodes/" + str(visitor.id) + "_" + str(hash(visitor.name)) + ".png"
		img.save(qrpath)
		
		return qrpath, token
	elif qrtype == 'details':
		visitor = VisitorsDetail.objects.get(id=id)
		token = str(visitor.name).upper() + ' ' + str(visitor.visitor.id) + '-' + str(visitor.id) + ' (V)'
		qr.add_data(token)
		qr.make(fit=True)
		img = qr.make_image(fill_color="black", back_color="white")
		qrpath = "./media/qrcodes/" + str(visitor.visitor.id) + "-" + str(visitor.id) + "_" + str(hash(visitor.name)) + ".png"
		img.save(qrpath)
		return qrpath

@csrf_exempt
@login_required()
@user_passes_test(is_security)
def scanQR(request, **kwargs):
	display_visitors = Visitor.objects.filter(session_expired=False)
	frame = base64.b64decode(request.POST['imgdata'])
	frame = BytesIO(frame)
	frame = Image.open(frame)
	Read = pb.decode(frame)
	for ob in Read:
		readData = str(ob.data.rstrip().decode('utf-8'))
		print('readData',readData)
		visitor = display_visitors.filter(token=readData).first()
		if visitor:
			if not visitor.in_time and visitor.expected_in_time:
				return redirect('/photoscan/' + str(visitor.id))
			elif visitor.in_time and not visitor.out_time:
				visitor.out_time = datetime.now()
				visitor.save()
				messages.success(request, f'Visitor has left')
				return redirect('/')
	messages.error(request, f'Invalid Token Scanned!')
	return redirect('/')
	
		
def send_normal_email(Visitor):
	to_email = Visitor.user.email
	if Visitor.out_time:
		subject = Visitor.name + ' has left Atlas Copco Campus'
		message = 'Hello!\n\n\t' + Visitor.name + ' has left the Atlas Copco campus at ' + str(Visitor.out_time.date()) + ' ' + str(Visitor.out_time.strftime("%X")) + '.'
	else:
		subject = Visitor.name + ' is visiting Atlas Copco'
		message = 'Hello!\n\n\t' + Visitor.name + ' is visiting the Atlas Copco campus at ' + str(Visitor.in_time.date()) + ' ' + str(Visitor.in_time.strftime("%X")) + 'with ' + str(Visitor.actual_visitors) + '.'
	email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [to_email])
	email.content_subtype='html'
	email.send(fail_silently=False)

def send_qrcode_email(to_email, qrcodeimg):
	subject = 'QR Code for entry in Atlas Copco'
	message = '''Hello!\nYou have been granted the permission to visit Atlas Copco as a visitor!\n 
			PFA an attached QR Code which you will have to show when you leave our premises!'''
	email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [to_email])
	email.content_subtype='html'
	with open(os.path.join(settings.BASE_DIR, '') + qrcodeimg, mode='rb') as file:
		email.attach(os.path.join(settings.BASE_DIR, '') + qrcodeimg, file.read(), 'image/png')
	
	email.send(fail_silently=False)
	
class VisitorUpdateView(LoginRequiredMixin, UpdateView):
	model = Visitor
	fields = ['name', 'purpose', 'no_of_people', 'email', 'mobile', 'user']
	success_url = reverse_lazy('home')
	template_name = 'entry/visitor_booking.html'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data()
		context['employees'] = User.objects.all()
		
		return context