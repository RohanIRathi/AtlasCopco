from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from .forms import CreateUserForm,CreateEmployeeForm
from entry.models import *


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
            messages.success(request, 'Account was created '  )
            return redirect('/login/')
    form = CreateUserForm()
    employee_form = CreateEmployeeForm()
    context = {'form': form, 'employee_form': employee_form}
    return render(request, 'registration/signup.html',context)


def login_validate(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username, password=password)
        if user is not None:
            print('User')
            login(request, user)
            return redirect('/')
        else:
            print('Not a User')
            messages.info(request, "Username or Password incorrect !")

    return render(request, 'registration/login.html')
