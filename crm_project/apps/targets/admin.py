from django.contrib import admin
from .models import Target, TargetSuggestion

@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ['assigned_to', 'target_amount', 'achieved_amount', 'month', 'year', 'status']
    list_filter = ['status', 'year', 'month', 'assigned_by']
    search_fields = ['assigned_to__username', 'assigned_to__first_name']

@admin.register(TargetSuggestion)
class TargetSuggestionAdmin(admin.ModelAdmin):
    list_display = ['amount', 'usage_count', 'is_active', 'created_date']
    list_filter = ['is_active']