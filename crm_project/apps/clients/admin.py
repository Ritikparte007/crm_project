from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'business_name', 'project_status', 'assigned_to', 'date_added']
    list_filter = ['project_status', 'industry_type', 'assigned_to']
    search_fields = ['customer_name', 'business_name', 'business_email']
    readonly_fields = ['date_added', 'date_modified']