from entry.views import VisitorUpdateView
from django.urls import path, include
from . import views

app_name = 'entry'
urlpatterns = [
	path('newvisitor',views.new_visitor, name='new-visitor'),
	path('updatevisitor/<int:pk>/', views.VisitorUpdateView.as_view(), name="visitor-update"),
	path('scanQR/', views.scanQR, name='scanQR'),
]