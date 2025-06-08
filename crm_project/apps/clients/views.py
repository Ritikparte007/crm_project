# clients/views.py - Complete working file with all required functions

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.views import View
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, date
import json
import logging

from .models import Client, ProjectStatus
from .serializers import ClientSerializer, ClientListSerializer

# Add logging
logger = logging.getLogger(__name__)
User = get_user_model()


# clients/views.py - Updated client_list_view with debugging

@login_required
def dashboard_or_clients_view(request):
    """
    यह function check करता है कि user कहाँ से आया है
    /dashboard/ से आया = dashboard.html show करो
    /clients/ से आया = clients.html show करो
    """
    
    # आपका existing logic
    user = request.user
    today = datetime.now().date()
    
    print(f"DEBUG: Current user: {user.username}")
    print(f"DEBUG: Request path: {request.path}")
    
    # Today's clients
    todays_clients = Client.objects.filter(
        assigned_to=user,
        date_added__date=today
    ).order_by('-date_added')
    
    # Transferred clients
    transferred_clients = Client.objects.filter(
        assigned_to=user,
        transferred_to=user,
        date_modified__date=today
    ).exclude(added_by=user).order_by('-date_modified')
    
    # Stats
    stats = {
        'total_target': 'Rs.21000/ Rs.0',
        'month_metalized': Client.objects.filter(
            assigned_to=user,
            project_status='metalized',
            date_added__month=today.month,
            date_added__year=today.year
        ).count(),
        'today_callback': Client.objects.filter(
            assigned_to=user,
            project_status='call_back',
            date_added__date=today
        ).count(),
    }
    
    context = {
        'stats': stats,
        'todays_clients': todays_clients,
        'transferred_clients': transferred_clients,
        'user': user,
    }
    
    # यहाँ magic होता है! 🪄
    # Check करते हैं कि कौन सा template use करना है
    if '/dashboard/' in request.path:
        # Dashboard template use करो
        return render(request, 'dashboard/dashboard.html', context)
    else:
        # Clients template use करो  
        # सभी clients get करो (dashboard की तरह filter नहीं)
        all_clients = Client.objects.filter(assigned_to=user).order_by('-date_added')
        context['clients'] = all_clients
        return render(request, 'clients/clients.html', context)

@login_required
def client_list_view(request):
    """
    Web view for displaying the client list page (dashboard)
    """
    user = request.user
    today = datetime.now().date()
    
    print(f"DEBUG: Current user: {user.username}")
    print(f"DEBUG: Today's date: {today}")
    
    # Get ALL clients for this user first (for debugging)
    all_user_clients = Client.objects.filter(assigned_to=user)
    print(f"DEBUG: Total clients assigned to user: {all_user_clients.count()}")
    
    # Get today's clients with more detailed filtering
    todays_clients = Client.objects.filter(
        assigned_to=user,
        date_added__date=today
    ).order_by('-date_added')
    
    print(f"DEBUG: Today's clients count: {todays_clients.count()}")
    
    # Debug: Print each today's client
    for client in todays_clients:
        print(f"DEBUG: Client - {client.customer_name}, Date: {client.date_added}, Status: {client.project_status}")
    
    # Get transferred clients
    transferred_clients = Client.objects.filter(
        assigned_to=user,
        transferred_to=user,
        date_modified__date=today
    ).exclude(added_by=user).order_by('-date_modified')
    
    print(f"DEBUG: Transferred clients count: {transferred_clients.count()}")
    
    # Calculate dashboard statistics
    stats = {
        'total_target': 'Rs.21000/ Rs.0',
        'month_metalized': Client.objects.filter(
            assigned_to=user, 
            project_status='metalized',
            date_added__month=today.month,
            date_added__year=today.year
        ).count(),
        'today_callback': Client.objects.filter(
            assigned_to=user, 
            project_status='call_back',
            date_added__date=today
        ).count(),
        'total_clients': all_user_clients.count(),
        'todays_clients_count': todays_clients.count(),
    }
    
    print(f"DEBUG: Stats: {stats}")
    print("====================")
    
    context = {
        'stats': stats,
        'todays_clients': todays_clients,
        'transferred_clients': transferred_clients,
        'user': user,
        'debug_info': {
            'today': today,
            'total_clients': all_user_clients.count(),
            'todays_count': todays_clients.count(),
        }
    }
    
    print(f"DEBUG: Context keys: {context.keys()}")
    
    return render(request, 'dashboard/dashboard.html', context)

class ClientListCreateAPIView(generics.ListCreateAPIView):
    """
    API View for listing and creating clients with detailed error handling
    """
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Client.objects.filter(assigned_to=self.request.user).order_by('-date_added')
    
    def create(self, request, *args, **kwargs):
        """Handle client creation with detailed validation and error reporting"""
        try:
            # Log the incoming data for debugging
            logger.info(f"Received client creation request from user {request.user.username}")
            logger.info(f"Request data: {request.data}")
            
            with transaction.atomic():
                data = request.data.copy()
                
                # Validate required fields first
                required_fields = ['customer_name', 'business_name', 'business_address', 'primary_phone', 'total_amount']
                missing_fields = []
                
                for field in required_fields:
                    if not data.get(field) or str(data.get(field)).strip() == '':
                        missing_fields.append(field.replace('_', ' ').title())
                
                if missing_fields:
                    return Response({
                        'success': False,
                        'message': f'Missing required fields: {", ".join(missing_fields)}',
                        'errors': {field: ['This field is required.'] for field in missing_fields}
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Handle empty values
                for key, value in data.items():
                    if value == '' or value is None:
                        if key not in required_fields:
                            data[key] = None if key in ['project_handover_date', 'transferred_to'] else ''
                
                # Handle date conversion
                if data.get('project_handover_date'):
                    try:
                        handover_date = datetime.strptime(data['project_handover_date'], '%Y-%m-%d').date()
                        data['project_handover_date'] = handover_date
                    except ValueError as e:
                        logger.error(f"Date conversion error: {e}")
                        return Response({
                            'success': False,
                            'message': 'Invalid date format for project handover date. Use YYYY-MM-DD format.',
                            'errors': {'project_handover_date': ['Invalid date format']}
                        }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    data['project_handover_date'] = None
                
                # Handle phone number validation
                primary_phone = str(data.get('primary_phone', '')).strip()
                if primary_phone:
                    # Remove spaces and special characters for validation
                    clean_phone = ''.join(filter(str.isdigit, primary_phone))
                    if len(clean_phone) < 10 or len(clean_phone) > 15:
                        return Response({
                            'success': False,
                            'message': 'Phone number must be between 10-15 digits',
                            'errors': {'primary_phone': ['Invalid phone number length']}
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                # Handle numeric fields
                try:
                    if data.get('total_amount'):
                        data['total_amount'] = float(data['total_amount'])
                    if data.get('advance_amount'):
                        data['advance_amount'] = float(data['advance_amount'])
                    else:
                        data['advance_amount'] = 0
                except (ValueError, TypeError) as e:
                    logger.error(f"Numeric conversion error: {e}")
                    return Response({
                        'success': False,
                        'message': 'Invalid numeric values for amount fields',
                        'errors': {'total_amount': ['Must be a valid number']}
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Handle transfer if specified
                transferred_to_user = None
                assigned_user = request.user
                
                if data.get('transferred_to') and str(data.get('transferred_to')).strip():
                    try:
                        transferred_to_user = User.objects.get(id=data['transferred_to'])
                        assigned_user = transferred_to_user
                        data['project_status'] = 'transferred'
                    except (User.DoesNotExist, ValueError) as e:
                        logger.error(f"Transfer user error: {e}")
                        return Response({
                            'success': False,
                            'message': 'Invalid user selected for transfer',
                            'errors': {'transferred_to': ['User not found']}
                        }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    data.pop('transferred_to', None)
                
                # Set default values
                if not data.get('project_status'):
                    data['project_status'] = 'call_back'
                
                if not data.get('industry_type'):
                    data['industry_type'] = 'other'
                
                # Create the serializer with cleaned data
                serializer = self.get_serializer(data=data)
                
                if serializer.is_valid():
                    client = serializer.save(
                        assigned_to=assigned_user,
                        added_by=request.user,
                        transferred_to=transferred_to_user
                    )
                    
                    logger.info(f"Client created successfully: {client.id}")
                    
                    return Response({
                        'success': True,
                        'message': 'Client added successfully!',
                        'id': client.id,
                        'client_data': {
                            'customer_name': client.customer_name,
                            'business_name': client.business_name,
                            'primary_phone': client.primary_phone,
                            'project_status': client.project_status
                        }
                    }, status=status.HTTP_201_CREATED)
                else:
                    logger.error(f"Serializer validation errors: {serializer.errors}")
                    # Format validation errors for better display
                    formatted_errors = {}
                    error_messages = []
                    
                    for field, errors in serializer.errors.items():
                        formatted_errors[field] = errors
                        field_name = field.replace('_', ' ').title()
                        if isinstance(errors, list):
                            error_messages.extend([f"{field_name}: {error}" for error in errors])
                        else:
                            error_messages.append(f"{field_name}: {errors}")
                    
                    return Response({
                        'success': False,
                        'message': 'Validation failed: ' + '; '.join(error_messages),
                        'errors': formatted_errors,
                        'field_errors': serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
        except Exception as e:
            logger.error(f"Unexpected error in client creation: {str(e)}")
            return Response({
                'success': False,
                'message': f'Server error: {str(e)}',
                'error_type': type(e).__name__
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_team_members(request):
    """API endpoint for getting team members"""
    try:
        team_members = User.objects.filter(
            is_active=True
        ).exclude(id=request.user.id).order_by('first_name', 'last_name')
        
        team_members_data = []
        for member in team_members:
            full_name = member.get_full_name() or member.username
            team_members_data.append({
                'id': member.id,
                'name': full_name,
                'role': getattr(member, 'role', 'User'),
                'username': member.username
            })
        
        return Response({
            'success': True,
            'team_members': team_members_data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def client_stats_view(request):
    """API endpoint for getting client statistics"""
    try:
        user = request.user
        today = datetime.now().date()
        current_month = today.month
        current_year = today.year
        
        stats = {
            'total_clients': Client.objects.filter(assigned_to=user).count(),
            'todays_clients': Client.objects.filter(assigned_to=user, date_added__date=today).count(),
            'this_month_clients': Client.objects.filter(
                assigned_to=user,
                date_added__month=current_month,
                date_added__year=current_year
            ).count(),
            'metalized_clients': Client.objects.filter(assigned_to=user, project_status='metalized').count(),
            'callback_clients': Client.objects.filter(assigned_to=user, project_status='call_back').count(),
            'not_interested_clients': Client.objects.filter(assigned_to=user, project_status='not_interested').count(),
            'already_paid_clients': Client.objects.filter(assigned_to=user, project_status='already_paid').count(),
        }
        
        return Response({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_clients_today_view(request):
    """
    API endpoint for getting today's clients
    """
    try:
        user = request.user
        today = datetime.now().date()
        
        # Get today's clients
        todays_clients = Client.objects.filter(
            assigned_to=user,
            date_added__date=today
        ).order_by('-date_added')
        
        # Get transferred clients
        transferred_clients = Client.objects.filter(
            assigned_to=user,
            transferred_to=user,
            date_modified__date=today
        ).exclude(added_by=user).order_by('-date_modified')
        
        # Serialize the data
        todays_clients_data = []
        for client in todays_clients:
            todays_clients_data.append({
                'id': client.id,
                'customer_name': client.customer_name,
                'business_name': client.business_name,
                'primary_phone': client.primary_phone,
                'project_status': client.get_project_status_display(),
                'total_amount': float(client.total_amount),
                'date_added': client.date_added.strftime('%Y-%m-%d %H:%M')
            })
        
        transferred_clients_data = []
        for client in transferred_clients:
            transferred_clients_data.append({
                'id': client.id,
                'customer_name': client.customer_name,
                'business_name': client.business_name,
                'primary_phone': client.primary_phone,
                'project_status': client.get_project_status_display(),
                'transferred_from': client.added_by.get_full_name(),
                'total_amount': float(client.total_amount),
                'date_modified': client.date_modified.strftime('%Y-%m-%d %H:%M')
            })
        
        return Response({
            'success': True,
            'todays_clients': todays_clients_data,
            'transferred_clients': transferred_clients_data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        })


@csrf_exempt
@login_required
def update_client_status(request, client_id):
    """
    Update client status via AJAX
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            client = get_object_or_404(Client, id=client_id, assigned_to=request.user)
            
            new_status = data.get('status')
            if new_status in dict(Client.STATUS_CHOICES):
                client.project_status = new_status
                client.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Status updated to {client.get_project_status_display()}'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid status'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@csrf_exempt
@login_required
def transfer_client(request):
    """
    Transfer client to another user
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            client_id = data.get('client_id')
            transfer_to_id = data.get('transfer_to')
            reason = data.get('reason', '')
            
            client = get_object_or_404(Client, id=client_id, assigned_to=request.user)
            transfer_to_user = get_object_or_404(User, id=transfer_to_id)
            
            # Update client assignment
            client.transferred_to = transfer_to_user
            client.assigned_to = transfer_to_user
            client.project_status = 'transferred'
            client.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Client transferred to {transfer_to_user.get_full_name()} successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


# Debug view - Remove this after testing
@csrf_exempt
def debug_client_create(request):
    """Debug view to see what data is being sent"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            return JsonResponse({
                'received_data': data,
                'user': request.user.username if request.user.is_authenticated else 'Anonymous',
                'is_authenticated': request.user.is_authenticated,
                'data_types': {key: type(value).__name__ for key, value in data.items()}
            })
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'raw_body': request.body.decode('utf-8')[:500]  # First 500 chars
            })
    else:
        return JsonResponse({'method': request.method, 'path': request.path})