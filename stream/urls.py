from django.urls import path

from . import views

app_name='stream'

urlpatterns = [
    path('<int:pk>/', views.scan, name='index'),
    path('user/', views.scan, name='scanner', kwargs={'pk': 'scan'}),
]