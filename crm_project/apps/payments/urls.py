from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.PaymentListCreateView.as_view(), name='payment_list_create'),
    path('stats/', views.payment_stats_view, name='payment_stats'),
    path('my-metalized-clients/', views.my_metalized_clients_view, name='my_metalized_clients'),
]