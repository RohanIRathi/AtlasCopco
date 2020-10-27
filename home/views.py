from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.urls import reverse
from django.views.generic import ListView

from .forms import CreateUserForm, CreateEmployeeForm
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
