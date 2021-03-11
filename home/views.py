from datetime import datetime
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from PIL import Image
from django.views.generic import ListView, DetailView
import base64
from django.contrib.auth.models import User
import os

from .forms import *
from entry.models import *
from entry import views

def is_admin(user):
	admin = True
	try:
		admin = User.objects.get(username=user).is_superuser and User.objects.get(username=user).is_staff
	except:
		admin = False
	finally:
		return admin

def is_security(user):
	security = False
	try:
		security = not User.objects.get(username=user).is_superuser and User.objects.get(username=user).is_staff
	except:
		pass
	finally:
		return security

@login_required
@user_passes_test(is_admin)
def signup(request):
	form = CreateUserForm()
	if request.method == "POST":
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			if request.POST['email'].endswith('@atlascopco.com'):
				if request.POST['role'] == 'admin':
					user.is_active = True
					user.is_staff = True
					user.is_superuser = True
				elif request.POST['role'] == 'security':
					user.is_active = True
					user.is_staff = True
					user.is_superuser = False
				elif request.POST['role'] == 'employee':
					user.is_active = True
					user.is_staff = False
					user.is_superuser = False
			else:
				messages.error(request, f'Error! Invalid email! User must have an Atlas Copco email!')
				context = {'form': form}
				return render(request, 'registration/signup.html', context)
			user.save()
			user = form.cleaned_data.get('username')
			messages.success(request, 'Account was created ')
			return redirect('/vms/login/')
	# employee_form = CreateEmployeeForm()
	context = {'form': form,} # 'employee_form': employee_form}
	return render(request, 'registration/signup.html', context)

def employee_signup(request):
	form = CreateUserForm()
	if request.method == "POST":
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			if(request.POST['email'].endswith('@atlascopco.com')):
				user.is_active = False
				user.is_staff = False
				user.is_superuser = False
			else:
				messages.error(request, f'Error! Invalid email! Employee must have an Atlas Copco email!')
				context = {'form': form, 'employeesignup': True}
				return render(request, 'registration/signup.html', context)
			user.save()
			ref = request.META['wsgi.url_scheme'] + "://" + request.META['HTTP_HOST']
			send_request_email(user, ref)
			user = form.cleaned_data.get('username')
			messages.success(request, 'Account was created! Waiting to activate your account!')
			return redirect('/vms/login/')
	# employee_form = CreateEmployeeForm()
	context = {'form': form, 'employeesignup': True} # 'employee_form': employee_form}
	return render(request, 'registration/signup.html', context)

def send_request_email(user, host):
	token = str(hash(user.last_name)) + '~' + str(user.id)
	mail_details = {
		'token': token,
		'first_name': user.first_name,
		'last_name': user.last_name,
		'host': host,
	}
	to_email = []
	admins = User.objects.filter(is_superuser=True).filter(is_staff=True)
	for admin in admins:
		to_email.append(admin.email)
	subject = "Request to create an account"
	html_message = render_to_string('registration/email.html', mail_details)
	message = strip_tags(html_message)
	from_email = settings.EMAIL_HOST_USER
	
	mail.send_mail(subject, message, from_email, to_email, html_message=html_message, fail_silently=False)

@login_required()
@user_passes_test(is_admin)
def accept_employee(request, token):
	try:
		pk = int(token.split('~')[1])
		user = User.objects.get(pk = pk)
		if str(token.split('~')[0]) == str(hash(user.last_name)):
			if not user.is_active:
				user.is_active = True
				user.save()
				subject = "Your account has been created!"
				message = "Your account has been approved! You can now log into your account using your email id and password."
				from_email = settings.EMAIL_HOST_USER
				to_email = user.email
				
				mail.send_mail(subject, message, from_email, [to_email], fail_silently=False)

				messages.success(request, f'Employee registered!')
			else:
				messages.info(request, f'The employee has been accepted by another admin')
			return redirect('/vms/')
		else:
			messages.error(request, f'Invalid link!')
			return redirect('/vms/')
	except:
		messages.error(request, f'No such user to validate!')
		return redirect('/vms/')

def login_validate(request):
	if request.method == "POST":
		user = User.objects.get(email=request.POST['username'])
		user_name = user.username
		password = request.POST['password']
		user = authenticate(request, username=user_name, password=password)
		if user is not None:
			print('User')
			login(request, user)
			if user.is_superuser or user.is_staff:
				return redirect(request.GET.get('next', 'home'))
			else:
				return redirect(reverse('entry:new-visitor'))
		else:
			print('Not a User')
			messages.error(request, "Username or Password incorrect !")

	return render(request, 'registration/login.html')

@login_required
def logout_user(request):
	logout(request)
	return redirect('/vms/')


class VisitorListView(LoginRequiredMixin, ListView):
	def get(self, request):
		if not request.user.is_staff and not request.user.is_superuser:
			return redirect('/entry/newvisitor')
		all = Visitor.objects.all()
		for visitor in all:
			if visitor.expected_in_time:
				if visitor.expected_in_time.date() < datetime.now().date() and not visitor.in_time:
					visitor.session_expired = True
					visitor.save()
		display_visitors = Visitor.objects.filter(session_expired=False)
		visitor_list1 = display_visitors.filter(expected_in_time__contains=datetime.now().date()).filter(out_time__isnull=True).order_by('-expected_in_time')
		visitor_list2 = display_visitors.filter(in_time__contains=datetime.now().date()).filter(out_time__isnull=True).order_by('in_time')
		visitor_list = visitor_list1.union(visitor_list2)
		visitors = display_visitors.count()
		visited = display_visitors.filter(out_time__isnull=False).count()
		to_visit = display_visitors.filter(in_time__isnull=True).count()
		visiting = display_visitors.filter(in_time__isnull=False).filter(out_time__isnull=True).count()
		context = {'visitor_list': visitor_list,  'visitor_count': visitors, 'visited_count': visited, 'not_visited_count': to_visit, 'visiting_count': visiting}

		return render(request, 'home/home.html', context)

class NotVisitedListView(LoginRequiredMixin, ListView):
	def get(self, request):
		display_visitors = Visitor.objects.filter(session_expired=False)
		visitor_list = display_visitors.filter(in_time__isnull=True)
		context = {'visitor_list': visitor_list}

		return render(request, 'home/not_visited.html', context)


def expiredBooking(request):
	expired = Visitor.objects.filter(session_expired=True)
	context = {'visitor_list': expired}
	if request.method == 'POST':
		search_query = request.POST['search']
		search_date = ''
		try:
			search_date = datetime.strptime(search_query, '%d-%m-%Y')
			print(search_date)
		except:
			pass
		try:
			user = User.objects.get(username__icontains=search_query)
		except:
			user = None
		visitor_list_employee = expired.filter(user=user)
		if search_date:
			visitor_list_intime = expired.filter(expired_in_time__date = search_date)
		else:
			visitor_list_intime = expired.filter(user=None)
		visitor_list_name = expired.filter(name__icontains=search_query)
		visitor_list = visitor_list_employee.union(visitor_list_intime, visitor_list_name)
		if search_query == '':
			visitor_list = expired
		context = {'visitor_list': visitor_list, 'search_query': search_query}
	else:
		visitor_list = expired


	return render(request, 'home/expired_booking.html', context)

class AllVisitedListView(LoginRequiredMixin, ListView):
	def get(self, request):
		display_visitors = Visitor.objects.filter(session_expired=False)
		visitor_list = display_visitors.filter(out_time__isnull = False).order_by('-in_time')
		context = {'visitor_list': visitor_list}

		return render(request, 'home/all_visitors.html', context)

class VisitorDetailView(LoginRequiredMixin, DetailView):
	model = Visitor
	template_name = 'home/visitor_view.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		print(context['visitor'].in_time)

		return context

@login_required
@user_passes_test(is_security)
def photoscan(request, **kwargs):
	if request.user.is_staff and not request.user.is_superuser:
		instance = get_object_or_404(Visitor, pk = kwargs.get('id'))
		visitorcount = VisitorsDetail.objects.filter(visitor=instance).count()
		if instance.actual_visitors:
			if instance.actual_visitors <= visitorcount and not instance.in_time:
				instance.in_time = datetime.now()
				views.send_normal_email(instance)
				instance.save()
				return redirect('/vms/')
		context = {'visitor': instance, 'current_visitor': (visitorcount+1)}
		if request.method == 'POST':
			if not instance.actual_visitors:
				if int(request.POST['actual_visitors']) > instance.no_of_people:
					messages.error(request, "These many visitors were not allowed!")
					return  render(request, 'home/photoscan.html', context)
				instance.actual_visitors = int(request.POST['actual_visitors'])
				instance.save()
			name = request.POST['name']
			email = request.POST['email']
			photo = request.POST['photo']
			photo_id = request.POST['photo_id']
			mobile = request.POST['mobile']
			if name and email and photo and photo_id and mobile:
				visitorsdetail = VisitorsDetail.objects.create(name = name, email = email, mobile = mobile, safety_training = True, visitor = instance)
				photoField = visitorsdetail.photo
				photo_name = visitorsdetail.name + str(instance.token) + '.png'
				photo_path = os.path.join('photo/', photo_name)
				framephoto = base64.b64decode(photo)
				framephoto = BytesIO(framephoto)
				framephoto = Image.open(framephoto)
				buffer = BytesIO()
				framephoto.save(fp=buffer, format="PNG")
				photoImg = ContentFile(buffer.getvalue())
				photoField.save(photo_name, InMemoryUploadedFile(
					photoImg, None, photo_name, 'image/png', photoImg.size, None
				))
				photoField = visitorsdetail.photo_id
				photo_name = visitorsdetail.name + str(instance.token) + '.png'
				photo_path = os.path.join('photo_id/', photo_name)
				framephoto = base64.b64decode(photo)
				framephoto = BytesIO(framephoto)
				framephoto = Image.open(framephoto)
				buffer = BytesIO()
				framephoto.save(fp=buffer, format="PNG")
				photoImg = ContentFile(buffer.getvalue())
				photoField.save(photo_name, InMemoryUploadedFile(
					photoImg, None, photo_name, 'image/png', photoImg.size, None
				))
				visitorsdetail.save()
				qrcodeimg = views.generateQR(visitorsdetail.id, 'details')
				views.send_qrcode_email(visitorsdetail.email, qrcodeimg)
				os.remove(qrcodeimg)
				if int(instance.actual_visitors) < visitorcount:
					success_url = '/vms/'
				else:
					success_url = reverse('photoscan', kwargs={'id': kwargs.get('id')})
				return redirect(success_url, context)
			else:
				messages.error(request, f'Error!')
			context = {'visitor': instance, 'current_visitor': (visitorcount+1)}
		return  render(request, 'home/photoscan.html', context)
	else:
		return redirect('/vms/')

def pseudophotoscan(request, **kwargs):
	instance = Visitor.objects.get(pk=kwargs.get('id'))
	if not instance.in_time:
		instance.in_time = datetime.now()
		instance.save()
		views.send_normal_email(instance)
		return redirect('/vms/')

class AllVisitorsListView(LoginRequiredMixin, ListView):
	def get(self, request):
		display_visitors = Visitor.objects.filter(session_expired=False)
		visitor_list = display_visitors.order_by('-in_time')
		context = {'visitor_list': visitor_list}

		return render(request, 'home/all_visitors_booked.html', context)



@login_required()
@user_passes_test(is_admin)
def get_table_data(request):
	display_visitors = Visitor.objects.filter(session_expired=False)
	search_query = ''
	if request.method == 'POST':
		search_query = request.POST['search']
		search_date = ''
		try:
			search_date = datetime.strptime(search_query, '%d-%m-%Y')
			print(search_date)
		except:
			pass
		try:
			user = User.objects.get(username__icontains=search_query)
		except:
			user = None
		visitor_list_employee = display_visitors.filter(user=user)
		if search_date:
			visitor_list_intime = display_visitors.filter(in_time__date = search_date)
		else:
			visitor_list_intime = display_visitors.filter(user=None)
		visitor_list_name = display_visitors.filter(name__icontains=search_query)
		visitor_list = visitor_list_employee.union(visitor_list_intime, visitor_list_name)
		print(visitor_list)
		if search_query == '':
			visitor_list = display_visitors.order_by('-in_time')
	else:
		visitor_list = display_visitors.order_by('-in_time')

	context = {'visitor_list': visitor_list, 'search_query': search_query}

	return render(request, 'home/table.html', context=context)


@user_passes_test(is_admin)
@login_required()
def visitor_in(request):
	display_visitors = Visitor.objects.filter(session_expired=False)
	visitor_list = display_visitors.filter(in_time__isnull=False).filter(out_time__isnull=True)
	context = {'visitor_list': visitor_list}
	return render(request, 'home/visitor_in.html',context)