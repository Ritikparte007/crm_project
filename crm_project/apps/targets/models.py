from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Target(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('completed', 'Completed'),
    ]
    
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_targets')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_targets')
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    achieved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    month = models.IntegerField()  # 1-12
    year = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    date_added = models.DateTimeField(auto_now_add=True)
    
    @property
    def achievement_percentage(self):
        if self.target_amount > 0:
            return (self.achieved_amount / self.target_amount) * 100
        return 0
    
    def __str__(self):
        return f"{self.assigned_to.username} - {self.month}/{self.year} - Rs.{self.target_amount}"
    
    class Meta:
        unique_together = ['assigned_to', 'month', 'year']
        ordering = ['-year', '-month']

class TargetSuggestion(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    usage_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Rs.{self.amount}"
    
    class Meta:
        ordering = ['-usage_count', 'amount']