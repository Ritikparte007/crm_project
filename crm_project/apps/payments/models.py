from django.db import models
from django.contrib.auth import get_user_model
from apps.clients.models import Client

User = get_user_model()

class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('metalized', 'Metalized Payment'),
        ('bonus', 'Bonus Payment'),
        ('executive', 'Executive Payment'),
        ('advance', 'Advance Payment'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='payments')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    remarks = models.TextField(blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    @property
    def payment_ratio(self):
        if self.total_amount > 0:
            return f"{self.amount_paid}/{self.total_amount}"
        return "0/0"
    
    def __str__(self):
        return f"{self.client.customer_name} - {self.payment_type} - {self.amount_paid}"
    
    class Meta:
        ordering = ['-date_added']