from django.shortcuts import redirect, render
from entry.models import User
from django.contrib.auth import authenticate
from .forms import LoginForm

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
            return render(request, "registration/login.html", {'form':form})
    else:
        return render(request, 'registration/login.html', {'form':form})