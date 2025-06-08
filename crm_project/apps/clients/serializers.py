# clients/serializers.py - Fixed version
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Client, ProjectStatus
import re

User = get_user_model()


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for Client model with comprehensive validation"""
    
    # Read-only fields that will be auto-populated
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    added_by_name = serializers.CharField(source='added_by.get_full_name', read_only=True)
    transferred_to_name = serializers.CharField(source='transferred_to.get_full_name', read_only=True)
    
    # Display choices for frontend
    project_status_display = serializers.CharField(source='get_project_status_display', read_only=True)
    industry_type_display = serializers.CharField(source='get_industry_type_display', read_only=True)
    
    class Meta:
        model = Client
        fields = [
            'id', 'customer_name', 'business_name', 'business_address',
            'primary_phone', 'secondary_phone', 'business_email', 'gst_number',
            'industry_type', 'industry_type_display', 'work_required', 
            'project_handover_date', 'remarks', 'project_status', 'project_status_display',
            'total_amount', 'advance_amount', 'assigned_to', 'assigned_to_name',
            'transferred_to', 'transferred_to_name', 'added_by', 'added_by_name',
            'date_added', 'date_modified'
        ]
        # Make these fields read-only so they don't require validation from frontend
        read_only_fields = ['id', 'date_added', 'date_modified', 'added_by', 'assigned_to']
    
    def validate_customer_name(self, value):
        """Validate customer name"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Customer name must be at least 2 characters long")
        return value.strip().title()
    
    def validate_business_name(self, value):
        """Validate business name"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Business name must be at least 2 characters long")
        return value.strip()
    
    def validate_business_address(self, value):
        """Validate business address"""
        if not value or len(value.strip()) < 5:
            raise serializers.ValidationError("Business address must be at least 5 characters long")
        return value.strip()
    
    def validate_primary_phone(self, value):
        """Validate primary phone number"""
        if not value:
            raise serializers.ValidationError("Primary phone is required")
            
        # Remove spaces, dashes, parentheses for validation
        clean_phone = re.sub(r'[\s\-\(\)\+]', '', str(value))
        
        # Check if it contains only digits
        if not clean_phone.isdigit():
            raise serializers.ValidationError("Phone number should contain only digits")
        
        # Check length
        if len(clean_phone) < 10 or len(clean_phone) > 15:
            raise serializers.ValidationError("Phone number must be between 10-15 digits")
        
        # Check for Indian phone number pattern
        if len(clean_phone) == 10 and not clean_phone[0] in '6789':
            raise serializers.ValidationError("Indian mobile number should start with 6, 7, 8, or 9")
        
        return value
    
    def validate_secondary_phone(self, value):
        """Validate secondary phone number if provided"""
        if value and value.strip():
            clean_phone = re.sub(r'[\s\-\(\)\+]', '', str(value))
            if not clean_phone.isdigit() or len(clean_phone) < 10 or len(clean_phone) > 15:
                raise serializers.ValidationError("Invalid secondary phone number format")
        return value
    
    def validate_business_email(self, value):
        """Validate business email if provided"""
        if value and value.strip():
            email_regex = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
            if not email_regex.match(value.strip()):
                raise serializers.ValidationError("Invalid email format")
            return value.strip().lower()
        return value
    
    def validate_gst_number(self, value):
        """Validate GST number format if provided"""
        if value and value.strip():
            # Basic GST validation - 15 characters
            gst_value = value.strip().upper()
            if len(gst_value) != 15:
                raise serializers.ValidationError("GST number must be 15 characters long")
            return gst_value
        return value
    
    def validate_total_amount(self, value):
        """Validate total amount"""
        if not value:
            raise serializers.ValidationError("Total amount is required")
        
        try:
            amount = float(value)
            if amount <= 0:
                raise serializers.ValidationError("Total amount must be greater than 0")
            if amount > 10000000:  # 1 Crore limit
                raise serializers.ValidationError("Total amount cannot exceed 1 Crore")
            return amount
        except (ValueError, TypeError):
            raise serializers.ValidationError("Total amount must be a valid number")
    
    def validate_advance_amount(self, value):
        """Validate advance amount"""
        if value is None or value == '':
            return 0
        
        try:
            amount = float(value)
            if amount < 0:
                raise serializers.ValidationError("Advance amount cannot be negative")
            return amount
        except (ValueError, TypeError):
            raise serializers.ValidationError("Advance amount must be a valid number")
    
    def validate_work_required(self, value):
        """Validate work required field"""
        if value and len(value.strip()) > 200:
            raise serializers.ValidationError("Work required description is too long (max 200 characters)")
        return value.strip() if value else ''
    
    def validate_remarks(self, value):
        """Validate remarks field"""
        if value and len(value.strip()) > 1000:
            raise serializers.ValidationError("Remarks is too long (max 1000 characters)")
        return value.strip() if value else ''
    
    def validate_project_status(self, value):
        """Validate project status"""
        if not value:
            return 'call_back'  # Default value
        
        valid_statuses = [choice[0] for choice in Client.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid project status. Must be one of: {', '.join(valid_statuses)}")
        return value
    
    def validate_industry_type(self, value):
        """Validate industry type"""
        if not value:
            return 'other'  # Default value
        
        valid_types = [choice[0] for choice in Client.INDUSTRY_CHOICES]
        if value not in valid_types:
            raise serializers.ValidationError(f"Invalid industry type. Must be one of: {', '.join(valid_types)}")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        # Check if advance amount doesn't exceed total amount
        total_amount = data.get('total_amount')
        advance_amount = data.get('advance_amount', 0)
        
        if total_amount and advance_amount and float(advance_amount) > float(total_amount):
            raise serializers.ValidationError({
                'advance_amount': 'Advance amount cannot be greater than total amount'
            })
        
        # Note: Removed project_handover_date validation as it's optional
        # and can be set to any date based on business requirements
        
        return data


class ClientListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for client lists"""
    
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    project_status_display = serializers.CharField(source='get_project_status_display', read_only=True)
    
    class Meta:
        model = Client
        fields = [
            'id', 'customer_name', 'business_name', 'primary_phone',
            'project_status', 'project_status_display', 'assigned_to_name',
            'total_amount', 'advance_amount', 'date_added'
        ]


class ProjectStatusSerializer(serializers.ModelSerializer):
    """Serializer for ProjectStatus model"""
    
    client_name = serializers.CharField(source='client.customer_name', read_only=True)
    added_by_name = serializers.CharField(source='added_by.get_full_name', read_only=True)
    
    class Meta:
        model = ProjectStatus
        fields = [
            'id', 'client', 'client_name', 'added_by', 'added_by_name',
            'verification_month_year', 'frontend_status', 'backend_status',
            'verification_status', 'verification_details', 'actions_required',
            'date_added'
        ]
        read_only_fields = ['id', 'date_added', 'added_by']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (for team member dropdown)"""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'email']


# Additional serializers for specific use cases

class ClientStatsSerializer(serializers.Serializer):
    """Serializer for client statistics"""
    
    total_clients = serializers.IntegerField()
    todays_clients = serializers.IntegerField()
    this_month_clients = serializers.IntegerField()
    metalized_clients = serializers.IntegerField()
    callback_clients = serializers.IntegerField()
    not_interested_clients = serializers.IntegerField()
    already_paid_clients = serializers.IntegerField()


class ClientTransferSerializer(serializers.Serializer):
    """Serializer for client transfer requests"""
    
    client_id = serializers.IntegerField()
    transfer_to = serializers.IntegerField()
    reason = serializers.CharField(max_length=500)
    
    def validate_client_id(self, value):
        try:
            client = Client.objects.get(id=value)
            return value
        except Client.DoesNotExist:
            raise serializers.ValidationError("Client not found")
    
    def validate_transfer_to(self, value):
        try:
            user = User.objects.get(id=value, is_active=True)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found or inactive")
    
    def validate_reason(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Reason must be at least 10 characters long")
        return value.strip()


class ClientStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating client status"""
    
    status = serializers.ChoiceField(choices=Client.STATUS_CHOICES)
    notes = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    
    def validate_notes(self, value):
        if value:
            return value.strip()
        return value