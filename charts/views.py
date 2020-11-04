from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from entry.models import Visitor

@login_required
def home(request):
    return render(request, 'charts/home.html')

@login_required
def visitor_chart(request):
    labels = []
    data = []
    for i in range(7):
        c = datetime.today() - timedelta(days=i + 1)
        d = datetime.today() - timedelta(days=i)
        labels.append(d.strftime("%d-%m-%Y"))
        data.append(Visitor.objects.filter(in_time__range=[c, d]).count())
    print(labels)
    print(data)
    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })