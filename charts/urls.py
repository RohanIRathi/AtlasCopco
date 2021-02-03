from django.urls import path
from . import views
app_name = 'charts'
urlpatterns = [
    path('show_charts-weekly/', views.home1, name='show-charts1'),
    path('show_charts-monthly/', views.home2, name='show-charts2'),
    path('show_charts-yearly/', views.home3, name='show-charts3'),
    path('visitor_chart1/', views.visitor_chart1, name='visitor-chart1'),
    path('visitor_chart2/', views.visitor_chart2, name='visitor-chart2'),
    path('visitor_chart3/', views.visitor_chart3, name='visitor-chart3'),
]