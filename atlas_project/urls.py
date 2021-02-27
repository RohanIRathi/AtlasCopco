from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [

    path('vms/admin/', admin.site.urls),
    path('vms/', include('home.urls')),
    path('vms/entry/',include('entry.urls')),
    path('vms/charts/', include('charts.urls')),

]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)