from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class User(AbstractUser):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('team_leader', 'Team Leader'),
        ('executive', 'Executive'),
        ('managing_director', 'Managing Director'),
        ('backend_team', 'Backend Team'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='executive')
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')],
        blank=True
    )
    employee_id = models.CharField(max_length=10, unique=True, null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

class UserProfile(models.Model):
    ACCOUNT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    alias_name = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=50, blank=True)
    branch_address = models.TextField(blank=True)
    reporting_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='subordinates'
    )
    account_status = models.CharField(
        max_length=20, 
        choices=ACCOUNT_STATUS_CHOICES, 
        default='active'
    )
    signup_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} Profile"