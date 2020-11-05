from django.urls import path
from . import views
app_name = 'charts'
urlpatterns = [
    path('show_charts/', views.home, name='show-charts'),
    path('charts_page1/', views.page1, name='chart-page1'),
    path('charts_page/', views.page, name='chart-page'),
    path('visitor_chart/', views.visitor_chart, name='visitor-chart'),
]