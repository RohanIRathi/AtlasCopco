from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate
from .forms import LoginForm,SignupForm
from entry.models import *


def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['mail']
        password = request.POST['pass']
        confirm_password = request.POST['password']
        role = request.POST['role']
        if password != confirm_password:
            messages.info(request, 'Passwords not matching!')
            return redirect(request.path)
        elif User.objects.filter(username=username).exists():
            messages.info(request,'Username taken!')
            return redirect(request.path)
        elif User.objects.filter(email=email).exists():
            messages.info(request,'Email already exists!')
            return redirect(request.path)
        else:
            user = User(username=username, email=email, password=password)
            user.save()
            print("New User created")
            messages.success(request,'New User created for '+username)
            return redirect('/')

    return render(request, 'registration/signup.html')


def login(request):
    form = LoginForm(request.POST)
    if request.method == 'POST':
        user = User.objects.get(email=(request.POST.get('mail')).lower())
        if request.POST.get('pass1') == user.password.rstrip():
            print('success')
            return redirect('/')
        else:
            form = LoginForm()
            print('No success\n\n')
            return render(request, "registration/login.html", {'form': form})
    else:
        return render(request, 'registration/login.html', {'form': form})
