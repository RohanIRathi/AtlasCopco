from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from entry.models import Visitor

@login_required
def home(request):
    return render(request, 'charts/home.html')

@login_required
def page(request):
    return render(request, 'charts/chart.html')

@login_required
def page1(request):
    return render(request, 'charts/chart1.html')

@login_required
def visitor_chart(request):
    labels = []
    data = []
    for i in range(7):
        d = datetime.today() - timedelta(days=i)
        labels.append(d.strftime("%d-%m-%Y"))
        data.append(Visitor.objects.filter(in_time__date=d.date()).count())
    print(labels)
    print(data)
    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })