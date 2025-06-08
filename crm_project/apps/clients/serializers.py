from rest_framework import serializers
from .models import Client
from apps.accounts.serializers import UserSerializer

class ClientSerializer(serializers.ModelSerializer):
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)
    transferred_to_detail = UserSerializer(source='transferred_to', read_only=True)
    added_by_detail = UserSerializer(source='added_by', read_only=True)
    
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ['date_added', 'date_modified']

class ClientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ['date_added', 'date_modified', 'added_by']

class ProjectStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'customer_name', 'project_status']