from datetime import datetime
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.urls import reverse
from django.urls.base import reverse_lazy
from django.views.generic import ListView, DetailView
from django.conf import settings
from django.db.models.query import QuerySet
import os

from .forms import *
from entry.models import *

def is_admin(user):
	try:
		admin = Employee.objects.get(user=user.id).admin
		return admin
	except:
		return False

@login_required
@user_passes_test(is_admin)
def signup(request):
	if request.method == "POST":
		form = CreateUserForm(request.POST)
		employee_form = CreateEmployeeForm(request.POST)
		if form.is_valid() and employee_form.is_valid():
			user = form.save()
			employee = employee_form.save(commit=False)
			employee.user = user
			employee.save()
			user = form.cleaned_data.get('username')
			messages.success(request, 'Account was created ')
			return redirect('/login/')
	form = CreateUserForm()
	employee_form = CreateEmployeeForm()
	context = {'form': form, 'employee_form': employee_form}
	return render(request, 'registration/signup.html', context)


def login_validate(request):
	if request.method == "POST":
		user_name = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=user_name, password=password)
		if user is not None:
			print('User')
			login(request, user)
			return redirect(request.GET.get('next', 'home'))
		else:
			print('Not a User')
			messages.info(request, "Email or Password incorrect !")

	return render(request, 'registration/login.html')

@login_required
def logout_user(request):
	logout(request)
	return redirect('/')


class VisitorListView(LoginRequiredMixin, ListView):
	def get(self, request):
		visitor_list = Visitor.objects.filter(out_time__isnull=True)
		print(visitor_list)
		context = {'visitor_list': visitor_list}

		return render(request, 'home/home.html', context)

class NotVisitedListView(LoginRequiredMixin, ListView):
	def get(self, request):
		visitor_list = Visitor.objects.filter(in_time__isnull=True)
		context = {'visitor_list': visitor_list}

		return render(request, 'home/not_visited.html', context)

class AllVisitedListView(LoginRequiredMixin, ListView):
	def get(self, request):
		visitor_list = Visitor.objects.filter(out_time__isnull = False).order_by('-in_time')
		context = {'visitor_list': visitor_list}

		return render(request, 'home/all_visitors.html', context)

class VisitorDetailView(LoginRequiredMixin, DetailView):
	model = Visitor
	template_name = 'home/visitor_view.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		if context['visitor'].photo_id:
			context['photopath'] = os.path.relpath(str(context['visitor'].photo_id))

		return context

@login_required
def photoscan(request, **kwargs):
	instance = get_object_or_404(Visitor, pk = kwargs.get('id'))
	form = PhotoForm()
	if request.method == 'POST':
		form = PhotoForm(request.POST, request.FILES, instance=instance)
		if form.is_valid():
			form.save()
			success_url = reverse('entry:scanQR', kwargs={'id': kwargs.get('id')})
			return redirect(success_url)
	return  render(request, 'home/photoscan.html', {'form':form})

class AllVisitorsListView(LoginRequiredMixin, ListView):
	def get(self, request):
		visitor_list = Visitor.objects.order_by('-in_time')
		context = {'visitor_list': visitor_list}

		return render(request, 'home/all_visitors_booked.html', context)
	
class AllUsersListView(LoginRequiredMixin, ListView):
	def get(self, request):
		employee_list = Employee.objects.all()
		context = {'employee_list': employee_list}
		
		return render(request, 'home/all_users_list.html', context)
	
@login_required()
@user_passes_test(is_admin)
def get_table_data(request):
	visitor_list = Visitor.objects.order_by('-in_time')
	search_query = ''
	if request.method == 'POST':
		search_query = request.POST['search']
		for i in [1]:
			print(visitor_list[1].in_time.date(), search_query)
			search_date = None
			sort = False
			try:
				search_date = datetime.strptime(search_query, '%d-%m-%Y')
				print(search_date)
			except:
				pass
			try:
				user = Employee.objects.get(user=User.objects.get(username__icontains=search_query))
				visitor_list = Visitor.objects.filter(user=user)
				if visitor_list:
					sort = True
			except:
				pass
			if search_date:
				visitor_list = Visitor.objects.filter(in_time__date = search_date)
			elif not sort:
				visitor_list = Visitor.objects.filter(name__icontains=search_query)
				print(visitor_list)
			else:
				break
		if search_query == '':
			visitor_list = Visitor.objects.order_by('-in_time')

	context = {'visitor_list': visitor_list, 'search_query': search_query}
	
	return render(request, 'home/table.html', context=context)