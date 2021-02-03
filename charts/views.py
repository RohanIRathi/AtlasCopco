from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncYear
from django.shortcuts import render
from django.http import JsonResponse
from entry.models import Visitor
from home.views import is_admin
@login_required
def home1(request):
    return render(request, 'charts/chart1.html')

@login_required
def home2(request):
    return render(request, 'charts/chart2.html')

@login_required
def home3(request):
    return render(request, 'charts/chart3.html')



@login_required
@user_passes_test(is_admin)
def visitor_chart1(request):
    labels = ['']
    data = [0]
    for i in range(7):
        d = datetime.today() - timedelta(days=i)
        labels.append(d.strftime("%d-%m-%Y"))
        data.append(Visitor.objects.filter(in_time__date=d.date()).count())
    labels.append('')
    data.append(0)
    print(labels,data)
    return JsonResponse(data={
        'labels': labels,
        'data': data,
        'scaletype': 'Days',
    })

@login_required
@user_passes_test(is_admin)
def visitor_chart2(request):
    labels = ['']
    data = [0]
    '''for i in range(30):
        d = datetime.today() - timedelta(months=i)
        labels.append(d.strftime("%d-%m-%Y"))
        data.append(Visitor.objects.filter(in_time__date=d.date()).count())
    print(labels)
    print(data)'''
    result = Visitor.objects.annotate(month=TruncMonth('in_time')).values('month').annotate(c=Count('id')).values('month', 'c')

    for i in result:
        try:
            labels.append(i['month'].strftime("%m-%Y"))
            data.append(i['c'])
        except:
            pass
    labels.append('')
    data.append(0)
    return JsonResponse(data={
        'labels': labels,
        'data': data,
        'scaletype': 'Months',
    })

@login_required
@user_passes_test(is_admin)
def visitor_chart3(request):
    labels = ['']
    data = [0]
    """for i in range(12):
        d = datetime.today() - timedelta(days=i)
        labels.append(d.strftime("%d-%m-%Y"))
        data.append(Visitor.objects.filter(in_time__date=d.date()).count())"""
    result = Visitor.objects.annotate(year=TruncYear('in_time')).values('year').annotate(c=Count('id')).values('year', 'c')

    for i in result:
        try:
            labels.append(i['year'].strftime("%Y"))
            data.append(i['c'])
        except:
            pass
    labels.append('')
    data.append(0)
    return JsonResponse(data={
        'labels': labels,
        'data': data,
        'scaletype':'Years',
    })