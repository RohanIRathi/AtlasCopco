from django.urls import path
from . import views
app_name = 'charts'
urlpatterns = [
    path('show_charts/', views.home, name='show-charts'),
    path('visitor_chart/', views.visitor_chart, name='visitor-chart'),
]