from django.urls import path
from . import views
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.login_validate, name='login'),
    path('signup/', views.signup, name='user-signup'),
    path('', views.VisitorListView.as_view(), name='home'),
    # path('test/', views.test, name='test'),
    path('logout/', views.logout_user, name='logout'),
]
