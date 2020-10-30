from home.views import AllVisitorsListView
from django.urls import path
from . import views
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', views.login_validate, name='login'),
    path('signup/', views.signup, name='user-signup'),
    path('', views.VisitorListView.as_view(), name='home'),
    path('notvisited/', views.NotVisitedListView.as_view(), name='not-visited'),
    path('allvisitors/', views.AllVisitorsListView.as_view(), name='all-visitors'),
    path('logout/', views.logout_user, name='logout'),

    # password reset urls
    path('reset_password/',
         auth_views.PasswordResetView.as_view(template_name='password/password_reset.html'),
         name='reset_password'),

    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(template_name='password/password_reset_sent.html'),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='password/password_reset_form.html'),
         name='password_reset_confirm'),

    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='password/password_reset_done.html'),
         name='password_reset_complete'),

]


