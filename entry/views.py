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
from django.core.exceptions import ObjectDoesNotExist

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
				visitor = form.save()
				qrcodeimg, visitor.token = generateQR(visitor.id)
				send_qrcode_email(visitor.email, qrcodeimg, visitor) # email to send the qr code to the visitor
				os.remove(qrcodeimg)
				visitor.actual_visitors = visitor.no_of_people
				visitor.save()
				messages.success(request, 'QR Code has been sent to the visitor\'s email-id')
				return redirect('/vms/')
			else:
				print(form.errors)
				messages.error(request, 'Error!')
		context = {'form': form, 'employees': employees}
		return render(request, 'entry/visitor_booking.html', context)
	else:
		return redirect('/vms/')


def generateQR(id, visitorcount=1):
	import qrcode
	display_visitors = Visitor.objects.filter(session_expired=False)
	qr = qrcode.QRCode(
		version=1,
		error_correction=qrcode.constants.ERROR_CORRECT_L,
		box_size=5,
		border=4
	)
	try:
		visitor = display_visitors.get(id=id)  # visitors id
	except ObjectDoesNotExist:
		visitor = VisitorsDetail.objects.get(id=id)
	token = str(visitor.name).upper() + '.' + str(visitorcount) + '-' + str(visitor.visitor.id) + '(V)'
	qr.add_data(token)
	qr.make(fit=True)
	img = qr.make_image(fill_color="black", back_color="white")
	qrpath = os.path.join(settings.BASE_DIR, "media/" + str(visitorcount) + "-" + str(visitor.id) + "_" + str(hash(visitor.name)) + ".png")
	img.save(qrpath)
	
	return qrpath, token

@csrf_exempt
@login_required()
@user_passes_test(is_security)
def scanQR(request, **kwargs):
	display_visitors = Visitor.objects.filter(session_expired=False)
	action = kwargs.get('action')
	print(action)
	frame = base64.b64decode(request.POST['imgdata'])
	frame = BytesIO(frame)
	frame = Image.open(frame)
	Read = pb.decode(frame)
	for ob in Read:
		frame.close()
		readData = str(ob.data.rstrip().decode('utf-8'))
		print('readData',readData)
		visitor_id = readData.split('-')[-1].split('(')[0]
		visitor = display_visitors.get(id=visitor_id)
		actualvisitors = visitor.actual_visitors or visitor.no_of_people
		if visitor:
			if action == 'add':
				visitorscount = VisitorsDetail.objects.filter(visitor=visitor).count()
				if visitorscount < actualvisitors:
					return redirect(f'/vms/photoscan/{visitor.id}/')
		if action == 'out':
			groupvisitor = VisitorsDetail.objects.filter(token=readData).first()
			if groupvisitor:
				if groupvisitor.in_time:
					groupvisitor.out_time = datetime.now()
					groupvisitor.save()
					messages.success(request, f'Visitor has left')
				gvisitorsleft = VisitorsDetail.objects.filter(visitor=visitor).filter(out_time__isnull=False).count()
				if gvisitorsleft == VisitorsDetail.objects.filter(visitor=visitor).count():
					visitor.out_time = datetime.now()
					send_normal_email(visitor)
					visitor.save()
				return redirect('/vms/')
	frame.close()
	messages.error(request, f'Invalid Token Scanned!')
	return redirect('/vms/')
	
		
def send_normal_email(Visitor):
	to_email = Visitor.user.email
	if Visitor.out_time:
		subject = Visitor.name + ' has left Atlas Copco Campus'
		message = 'Hello ' + str(Visitor.user.first_name) + '!\n\n\t' + Visitor.name + ' has left the Atlas Copco campus at ' + str(Visitor.out_time.date()) + ' ' + str(Visitor.out_time.strftime("%X")) + '.'
	else:
		subject = Visitor.name + ' is visiting Atlas Copco'
		message = 'Hello ' + str(Visitor.user.first_name) + '!\n\n\t' + Visitor.name + ' is visiting the Atlas Copco campus at ' + str(Visitor.in_time.date()) + ' ' + str(Visitor.in_time.strftime("%X")) + ' with ' + str(Visitor.actual_visitors) + ' visitors.'
	email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [to_email])
	email.content_subtype='html'
	email.send(fail_silently=False)

def send_qrcode_email(to_email, qrcodeimg, visitor):
	subject = 'QR Code for entry in Atlas Copco'
	message = 'Hello ' + str(visitor.name) + '!\nGreetings of the day!\n\tYou have been granted the permission to visit Atlas Copco by ' + str(visitor.user.first_name) + ' on ' + str(visitor.expected_in_time.date()) + ' ' + str(visitor.expected_in_time.strftime("%X")) + ' with ' + str(visitor.no_of_people) + ''' visitors.\n 
			PFA an attached QR Code which you will have to show when you leave our premises!'''
	email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [to_email], cc=[visitor.user.email])
	email.content_subtype='html'
	with open(qrcodeimg, mode='rb') as file:
		email.attach(qrcodeimg, file.read(), 'image/png')
	
	email.send(fail_silently=False)

def send_qrcode_email_details(to_email, qrcodeimg, visitor):
	subject = 'QR Code for entry in Atlas Copco'
	message = 'Hello ' + str(visitor.name) + '!\nGreetings of the day!\n\tYou have been granted the permission to visit Atlas Copco by ' + str(visitor.visitor.user.first_name) + ' on ' + str(visitor.visitor.expected_in_time.date()) + ' ' + str(visitor.visitor.expected_in_time.strftime("%X")) + ' with ' + str(visitor.visitor.actual_visitors) + ''' visitors.\n 
			PFA an attached QR Code which you will have to show when you leave our premises!'''
	email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [to_email])
	email.content_subtype='html'
	with open(qrcodeimg, mode='rb') as file:
		email.attach(qrcodeimg, file.read(), 'image/png')
	
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