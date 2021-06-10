from datetime import datetime, timedelta
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
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
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
			if request.user:
				return redirect('/vms/')
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
	token = urlsafe_base64_encode(force_bytes(str(datetime.now()) + '~' + str(user.id)))
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

@login_required
@user_passes_test(is_admin)
def accept_employee(request, token):
	try:
		# pk = int(token.split('~')[1])
		decoded = force_text(urlsafe_base64_decode(token))
		request_date = decoded.strip().split('~')[0]
		pk = decoded.split('~')[1]
		user = User.objects.get(pk = pk)
		if user and datetime.now() < request_date + timedelta(days=1):
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
	except (TypeError, ValueError, OverflowError, User.DoesNotExist):
		messages.error(request, f'No such user to validate!')
		return redirect('/vms/')

def login_validate(request):
	if request.method == "POST":
		if User.objects.filter(email=request.POST['username']).exists():
			user1 = User.objects.get(email=request.POST['username'])
			user_name = user1.username
			password = request.POST['password']
			user = authenticate(request, username=user_name, password=password)
			if user:
				login(request, user)
				if user.is_superuser or user.is_staff:
					return redirect(request.POST.get('next', '/vms/'))
				else:
					return redirect(reverse('entry:new-visitor'))
			elif not user1.is_active:
				messages.error(request, "User Not Approved Yet!")
			else:
				messages.error(request, "Incorrect Password!")
		else:
			messages.error(request, "Incorrect Email!")
		return redirect(str(request.get_full_path()) + '?next=' + str(request.POST.get('next', '/vms/')))

	return render(request, 'registration/login.html')

@login_required
def logout_user(request):
	logout(request)
	return redirect('/vms/')


class VisitorListView(LoginRequiredMixin, ListView):
	def get(self, request):
		if not request.user.is_staff and not request.user.is_superuser:
			return redirect('/vms/entry/newvisitor/')
		every = Visitor.objects.all()
		for visitor in every:
			if visitor.expected_in_time:
				if visitor.expected_in_time.date() < datetime.now().date() and not visitor.in_time:
					visitor.session_expired = True
				else:
					visitor.session_expired = False
				visitor.save()
		display_visitors = Visitor.objects.filter(session_expired=False)
		visitor_list1 = display_visitors.filter(expected_in_time__contains=datetime.now().date()).filter(out_time__isnull=True).order_by('-expected_in_time')
		visitor_list2 = display_visitors.filter(in_time__contains=datetime.now().date()).filter(out_time__isnull=True).order_by('in_time')
		visitor_list = visitor_list1.union(visitor_list2)
		home_visitors = []
		for visitor in visitor_list:
			visitordetails = []
			visitordetails.append(visitor)
			visitordetails.append(VisitorsDetail.objects.filter(visitor=visitor).count())
			home_visitors.append(visitordetails)
		visitors = display_visitors.count()
		visited = display_visitors.filter(out_time__isnull=False).count()
		to_visit = display_visitors.filter(in_time__isnull=True).count()
		visiting = VisitorsDetail.objects.filter(in_time__isnull=False).filter(out_time__isnull=True).count()
		context = {'visitor_list': home_visitors,  'visitor_count': visitors, 'visited_count': visited, 'not_visited_count': to_visit, 'visiting_count': visiting}

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

@login_required
@user_passes_test(is_admin)
def visitor_detail(request, **kwargs):
    pk = int(kwargs.get('pk'))
    visitorlist = VisitorsDetail.objects.filter(visitor = pk)
    visitor = Visitor.objects.get(id = pk)
    visitor_count = visitorlist.count()
    context = {'visitor_list': visitorlist, 'visitor': visitor, 'visitor_count': visitor_count}
    
    return render(request, 'home/visitor_view.html', context)

@login_required
@user_passes_test(is_security)
def photoscan(request, **kwargs):
	if request.user.is_staff and not request.user.is_superuser:
		instance = get_object_or_404(Visitor, pk = kwargs.get('id'))
		visitorcount = VisitorsDetail.objects.filter(visitor=instance).count()
		if instance.actual_visitors:
			if instance.actual_visitors <= visitorcount:
				return redirect('/vms/')
		context = {'visitor': instance, 'current_visitor': (visitorcount+1)}
		if request.method == 'POST':
			if int(request.POST['actual_visitors']) > instance.no_of_people:
				messages.error(request, "These many visitors were not allowed!")
				return  render(request, 'home/photoscan.html', context)
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
				if visitorcount == 0:
					visitorsdetail.token = instance.token
				else:
					qrcodeimg, visitorsdetail.token = views.generateQR(visitorsdetail.id, visitorcount+1)
					views.send_qrcode_email_details(visitorsdetail.email, qrcodeimg, visitorsdetail)
					os.remove(qrcodeimg)
				if int(instance.actual_visitors) < visitorcount:
					success_url = '/vms/'
				else:
					success_url = reverse('photoscan', kwargs={'id': kwargs.get('id')})
				instance.actual_visitors = int(request.POST['actual_visitors'])
				instance.in_time = datetime.now()
				instance.save()
				visitorsdetail.in_time = datetime.now()
				visitorsdetail.save()
				if visitorcount == 0:
					views.send_normal_email(instance)
				return redirect(success_url, context)
			else:
				if not photo:
					photoerror = "Photo Required"
					context['photoerror'] = photoerror
				if not photo_id:
					photoiderror = "Photo ID Required"
					context['photoiderror'] = photoiderror
		return  render(request, 'home/photoscan.html', context)
	else:
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
	visitor_list = VisitorsDetail.objects.filter(in_time__isnull=False).filter(out_time__isnull=True)
	context = {'visitor_list': visitor_list}
	return render(request, 'home/visitor_in.html',context)