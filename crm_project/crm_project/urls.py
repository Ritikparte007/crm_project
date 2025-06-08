# crm_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def redirect_to_dashboard(request):
    return redirect('/dashboard/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_dashboard),  # Home page pe dashboard खुलेगा
    path('dashboard/', include('apps.clients.urls')),  # Dashboard के लिए
    path('clients/', include('apps.clients.urls')),   # Clients के लिए
    path('api/auth/', include('apps.accounts.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/targets/', include('apps.targets.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)