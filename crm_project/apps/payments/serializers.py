from rest_framework import serializers
from .models import Payment
from apps.clients.serializers import ClientSerializer
from apps.accounts.serializers import UserSerializer

class PaymentSerializer(serializers.ModelSerializer):
    client_detail = ClientSerializer(source='client', read_only=True)
    added_by_detail = UserSerializer(source='added_by', read_only=True)
    payment_ratio = serializers.ReadOnlyField()
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['date_added']

class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['date_added', 'added_by']