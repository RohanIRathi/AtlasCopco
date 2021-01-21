from datetime import datetime, timedelta
from django.http import request
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
import os
from django.contrib.auth.models import User

from .forms import *
from entry.models import *

def is_admin(user):
	try:
		admin = User.objects.get(username=user).is_superuser
		return admin
	except:
		return False

@login_required
@user_passes_test(is_admin)
def signup(request):
	if request.method == "POST":
		form = CreateUserForm(request.POST)
		# employee_form = CreateEmployeeForm(request.POST)
		if form.is_valid() :  # and employee_form.is_valid():
			user = form.save()
			"""employee = employee_form.save(commit=False)
			employee.user = user
			employee.save()"""
			user = form.cleaned_data.get('username')
			messages.success(request, 'Account was created ')
			return redirect('/login/')
	form = CreateUserForm()
	# employee_form = CreateEmployeeForm()
	context = {'form': form,} # 'employee_form': employee_form}
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
			messages.error(request, "Username or Password incorrect !")

	return render(request, 'registration/login.html')

@login_required
def logout_user(request):
	logout(request)
	return redirect('/')


class VisitorListView(LoginRequiredMixin, ListView):
	def get(self, request):
		all = Visitor.objects.all()
		for visitor in all:
			if visitor.expected_in_time:
				if visitor.expected_in_time.date() < datetime.now().date() and not visitor.in_time:
					print(visitor.name)
					visitor.session_expired = True
					visitor.save()
		display_visitors = Visitor.objects.filter(session_expired=False)
		visitor_list = display_visitors.filter(expected_in_time__date=datetime.now().date()).filter(out_time__isnull=True)
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

class VisitExpiredListView(LoginRequiredMixin, ListView):
	def get(self, request):
		expired = Visitor.objects.filter(session_expired=True)
		context = {'visitor_list': expired}

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
		if context['visitor'].photo_id:
			context['photopath'] = os.path.relpath(str(context['visitor'].photo_id))

		return context

@login_required
def photoscan(request, **kwargs):
	instance = get_object_or_404(Visitor, pk = kwargs.get('id'))
	form = PhotoForm()
	context = {'form':form, 'visitor': instance}
	if request.method == 'POST':
		form = PhotoForm(request.POST, request.FILES, instance=instance)
		if form.is_valid():
			if request.POST['visit_token']:
				instance.visit_token = request.POST['visit_token']
				instance.save()
				messages.success(request, f'Visitor assigned token: { instance.visit_token }')
				success_url = '/'
			else:
				success_url = reverse('stream:index', kwargs={'pk': kwargs.get('id')})
			form.save()
			return redirect(success_url)
	return  render(request, 'home/photoscan.html', context)

@login_required
def take_visitor_token(request, **kwargs):
    instance = get_object_or_404(Visitor, pk = kwargs.get('id'))
    if request.method == 'POST':
        form = VisitorTokenForm(request.POST, instance=instance)
        if form.is_valid:
            token = request.POST['visit_token']
            form.save()
            messages.success(request, f'Visitor provided with token: { token }')
            return redirect('/')


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
	visitor_list = display_visitors.order_by('-in_time')
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
				user = User.objects.get(username__icontains=search_query)
				visitor_list = display_visitors.filter(user=user)
				if visitor_list:
					sort = True
			except:
				pass
			if search_date:
				visitor_list = display_visitors.filter(in_time__date = search_date)
			elif not sort:
				visitor_list = display_visitors.filter(name__icontains=search_query)
				print(visitor_list)
			else:
				break
		if search_query == '':
			visitor_list = display_visitors.order_by('-in_time')

	context = {'visitor_list': visitor_list, 'search_query': search_query}

	return render(request, 'home/table.html', context=context)



@login_required()
def visitor_in(request):
	display_visitors = Visitor.objects.filter(session_expired=False)
	visitor_list = display_visitors.filter(in_time__isnull=False).filter(out_time__isnull=True)
	context = {'visitor_list': visitor_list}
	return render(request, 'home/visitor_in.html',context)