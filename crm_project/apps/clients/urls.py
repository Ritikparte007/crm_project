from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    # Web views
    path('', views.client_list_view, name='client_list'),
    
    # API views
    path('api/', views.ClientListCreateView.as_view(), name='client_list_create'),
    path('api/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('api/stats/', views.client_stats_view, name='client_stats'),
    path('api/my-clients-today/', views.my_clients_today_view, name='my_clients_today'),
]