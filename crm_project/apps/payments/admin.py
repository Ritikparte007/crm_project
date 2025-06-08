from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['client', 'payment_type', 'amount_paid', 'payment_status', 'date_added']
    list_filter = ['payment_type', 'payment_status', 'date_added']
    search_fields = ['client__customer_name', 'client__business_name']
    readonly_fields = ['date_added']