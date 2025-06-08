# clients/models.py - Make sure your model matches this exactly

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()

class Client(models.Model):
    STATUS_CHOICES = [
        ('metalized', 'Metalized'),
        ('call_back', 'Call Back'),
        ('not_interested', 'Not Interested'),
        ('already_paid', 'Already Paid'),
        ('transferred', 'Transferred'),
    ]
    
    INDUSTRY_CHOICES = [
        ('web_design', 'Web Design & Development'),
        ('real_estate', 'Real Estate'),
        ('home_decor', 'Home Decor'),
        ('studio_accessories', 'Studio Accessories'),
        ('handloom', 'Handloom'),
        ('other', 'Other'),
    ]
    
    # Client Information
    customer_name = models.CharField(max_length=100)
    business_name = models.CharField(max_length=100)
    business_address = models.TextField()
    primary_phone = models.CharField(max_length=15)
    secondary_phone = models.CharField(max_length=15, blank=True, null=True)
    business_email = models.EmailField(blank=True, null=True)
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    industry_type = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, default='other')
    
    # Project Information
    work_required = models.CharField(max_length=200, blank=True, null=True)
    project_handover_date = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    project_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='call_back')
    
    # Assignment Information
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_clients')
    transferred_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='transferred_clients'
    )
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='added_clients')
    
    # Financial Information
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    
    # Timestamps
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.customer_name} - {self.business_name}"
    
    class Meta:
        ordering = ['-date_added']


class ProjectStatus(models.Model):
    FRONTEND_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]
    
    BACKEND_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]
    
    VERIFICATION_STATUS_CHOICES = [
        ('verified', 'Verified'),
        ('pending_verification', 'Pending Verification'),
        ('rejected', 'Rejected'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='project_statuses')
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    verification_month_year = models.CharField(max_length=20)
    frontend_status = models.CharField(max_length=20, choices=FRONTEND_STATUS_CHOICES, default='pending')
    backend_status = models.CharField(max_length=20, choices=BACKEND_STATUS_CHOICES, default='pending')
    verification_status = models.CharField(max_length=30, choices=VERIFICATION_STATUS_CHOICES, default='pending_verification')
    verification_details = models.TextField(blank=True, null=True)
    actions_required = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.client.customer_name} - {self.verification_month_year}"
    
    class Meta:
        ordering = ['-date_added']