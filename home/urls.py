from django.urls import path
from . import views
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.login_validate, name='login'),
    path('signup/', views.signup, name='user-signup'),
    path('', TemplateView.as_view(template_name='home/index.html'), name='home'),
    path('test/', views.test, name='test'),
    path('logout/', views.logout_user, name='logout'),
    path('home/', views.VisitorListView.as_view(), name='home'),
]
