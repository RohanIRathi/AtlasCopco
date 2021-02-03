from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def scan(request, pk):
    return render(request, 'stream/index.html', {'pk': pk})
