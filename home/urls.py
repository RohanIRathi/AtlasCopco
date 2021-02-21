from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
	path('login/', views.login_validate, name='login'),
	path('signup/', views.signup, name='user-signup'),
	path('signup/employee', views.employee_signup, name='employee_signup'),
	path('acceptemployee/<str:token>/', views.accept_employee, name='adminaccept'),
	path('', views.VisitorListView.as_view(), name='home'),
	path('expired/', views.expiredBooking, name='disabled'),
	path('notvisited/', views.NotVisitedListView.as_view(), name='not-visited'),
	path('allvisitors/', views.AllVisitedListView.as_view(), name='all-visitors'),
	path('edit/visitor/<int:pk>/', views.VisitorDetailView.as_view(), name='visitor-detail'),
	path('allbookedvisitors/', views.AllVisitorsListView.as_view(), name='all-booked-visitors'),
	path('logout/', views.logout_user, name='logout'),
	path('photoscan/<int:id>/', views.photoscan, name='photoscan'),
	path('photoscan/<int:id>/addlater/', views.pseudophotoscan, name='pseudophotoscan'),
	path('tables/', views.get_table_data, name='tables'),
	path('visitor_in/', views.visitor_in, name='visitor_in'),
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


