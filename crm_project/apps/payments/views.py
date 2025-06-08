from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum
from .models import Payment
from .serializers import PaymentSerializer, PaymentCreateSerializer

class PaymentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(added_by=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PaymentCreateSerializer
        return PaymentSerializer
    
    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_stats_view(request):
    user_payments = Payment.objects.filter(added_by=request.user)
    
    stats = {
        'total_payments': user_payments.count(),
        'metalized_payments': user_payments.filter(payment_type='metalized').count(),
        'total_amount_received': user_payments.aggregate(total=Sum('amount_paid'))['total'] or 0,
        'pending_payments': user_payments.filter(payment_status='pending').count(),
    }
    
    return Response(stats)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_metalized_clients_view(request):
    metalized_payments = Payment.objects.filter(
        added_by=request.user, 
        payment_type='metalized'
    ).select_related('client')
    
    serializer = PaymentSerializer(metalized_payments, many=True)
    return Response(serializer.data)