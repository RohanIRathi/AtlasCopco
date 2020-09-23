from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='user-signup'),
    path('', TemplateView.as_view(template_name='home/index.html'), name='home'),
]
