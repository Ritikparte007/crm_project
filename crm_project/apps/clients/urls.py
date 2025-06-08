# apps/clients/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard view (जब /dashboard/ से access करें)
    path('', views.dashboard_or_clients_view, name='dashboard_or_clients'),
    
    # API views (जो आपके पास already हैं)
    path('api/', views.ClientListCreateAPIView.as_view(), name='client_list_create'),
    path('api/stats/', views.client_stats_view, name='client_stats'),
    path('api/my-clients-today/', views.my_clients_today_view, name='my_clients_today'),
    path('api/team-members/', views.get_team_members, name='get_team_members'),
    path('api/update-status/<int:client_id>/', views.update_client_status, name='update_client_status'),
    path('api/transfer/', views.transfer_client, name='transfer_client'),
    path('api/debug/', views.debug_client_create, name='debug_client_create'),
]