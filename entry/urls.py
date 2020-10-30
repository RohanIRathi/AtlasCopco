from django.urls import path, include
from . import views

app_name = 'entry'
urlpatterns = [
    path('newvisitor',views.new_visitor, name='new-visitor'),
    path('scanQR/<int:id>', views.scanQR, name='scanQR'),
]