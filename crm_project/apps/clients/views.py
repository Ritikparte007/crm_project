from django.shortcuts import render
from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.utils import timezone
from .models import Client, ProjectStatus
from .serializers import ClientSerializer, ClientCreateSerializer, ProjectStatusSerializer

class ClientListCreateView(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project_status', 'industry_type', 'assigned_to', 'month_filter', 'year_filter']
    search_fields = ['customer_name', 'business_name', 'business_email', 'primary_phone']
    ordering_fields = ['date_added', 'customer_name', 'total_amount']
    ordering = ['-date_added']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ClientCreateSerializer
        return ClientSerializer
    
    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)

class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def client_stats_view(request):
    user = request.user
    today = timezone.now().date()
    
    stats = {
        'total_clients': Client.objects.filter(assigned_to=user).count(),
        'metalized': Client.objects.filter(assigned_to=user, project_status='metalized').count(),
        'call_back': Client.objects.filter(assigned_to=user, project_status='call_back').count(),
        'not_interested': Client.objects.filter(assigned_to=user, project_status='not_interested').count(),
        'transferred': Client.objects.filter(transferred_to=user).count(),
        'today_clients': Client.objects.filter(assigned_to=user, date_added__date=today).count(),
    }
    
    return Response(stats)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_clients_today_view(request):
    from django.utils import timezone
    today = timezone.now().date()
    clients = Client.objects.filter(assigned_to=request.user, date_added__date=today)
    serializer = ClientSerializer(clients, many=True)
    return Response(serializer.data)



def client_list_view(request):
    context = {
        'clients': [],
        'stats': {
            'total': 0,
            'metalized': 0,
            'call_back': 0,
            'not_interested': 0,
            'transferred': 0,
            'already_paid': 0,
        }
    }
    return render(request, 'clients/client_list.html', context)