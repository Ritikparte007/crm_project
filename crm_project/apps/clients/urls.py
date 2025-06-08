from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    # Web views
    path('', views.client_list_view, name='client_list'),
    
    # API views
    path('api/', views.ClientListCreateAPIView.as_view(), name='client_list_create'),
    path('api/stats/', views.client_stats_view, name='client_stats'),
    path('api/my-clients-today/', views.my_clients_today_view, name='my_clients_today'),
    path('api/team-members/', views.get_team_members, name='get_team_members'),
    path('api/update-status/<int:client_id>/', views.update_client_status, name='update_client_status'),
    path('api/transfer/', views.transfer_client, name='transfer_client'),
    
    # Debug endpoint - remove after testing
    path('api/debug/', views.debug_client_create, name='debug_client_create'),
]

# ===== MAIN PROJECT URLs =====
# crm_project/urls.py

"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def redirect_to_dashboard(request):
    return redirect('clients:dashboard')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Redirect root to dashboard
    path('', redirect_to_dashboard, name='home'),
    
    # App URLs
    path('clients/', include('clients.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Additional apps (when you create them)
    # path('targets/', include('targets.urls')),
    # path('payments/', include('payments.urls')),
    # path('api/auth/', include('accounts.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
"""


# ===== ADDITIONAL API VIEWS FOR COMPLETE FUNCTIONALITY =====

"""
Add these additional views to your clients/views.py:

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_clients(request):
    \"\"\"
    Search clients by name, phone, email, or business name
    \"\"\"
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return Response({
            'success': False,
            'message': 'Search query must be at least 2 characters',
            'results': []
        })
    
    clients = Client.objects.filter(
        Q(customer_name__icontains=query) |
        Q(business_name__icontains=query) |
        Q(primary_phone__icontains=query) |
        Q(business_email__icontains=query),
        assigned_to=request.user
    ).order_by('-date_added')[:20]
    
    serializer = ClientListSerializer(clients, many=True)
    
    return Response({
        'success': True,
        'results': serializer.data,
        'count': clients.count()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def filter_clients(request):
    \"\"\"
    Filter clients by various criteria
    \"\"\"
    clients = Client.objects.filter(assigned_to=request.user)
    
    # Apply filters
    status = request.GET.get('status')
    if status:
        clients = clients.filter(project_status=status)
    
    industry = request.GET.get('industry')
    if industry:
        clients = clients.filter(industry_type=industry)
    
    date_from = request.GET.get('date_from')
    if date_from:
        clients = clients.filter(date_added__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        clients = clients.filter(date_added__lte=date_to)
    
    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 25))
    
    from django.core.paginator import Paginator
    paginator = Paginator(clients, per_page)
    page_obj = paginator.get_page(page)
    
    serializer = ClientListSerializer(page_obj, many=True)
    
    return Response({
        'success': True,
        'results': serializer.data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        }
    })
"""


# ===== FRONTEND JAVASCRIPT UPDATES =====

"""
Update your HTML template JavaScript to use these endpoints:

<script>
// Update the team members loading function
function loadTeamMembers() {
    fetch('/clients/api/team-members/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        const transferSelect = document.getElementById('transferred_to');
        transferSelect.innerHTML = '<option value="">Transfer To Whom</option>';
        
        if (data.success && data.team_members) {
            data.team_members.forEach(member => {
                const option = document.createElement('option');
                option.value = member.id;
                option.textContent = `${member.name} (${member.role})`;
                transferSelect.appendChild(option);
            });
        }
    })
    .catch(error => {
        console.error('Error loading team members:', error);
    });
}

// Add search functionality
function searchClients(query) {
    if (query.length < 2) return;
    
    fetch(`/clients/api/search/?q=${encodeURIComponent(query)}`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displaySearchResults(data.results);
        }
    })
    .catch(error => {
        console.error('Search error:', error);
    });
}

// Add client status update function
function updateClientStatus(clientId, newStatus) {
    fetch(`/clients/api/update-status/${clientId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            status: newStatus,
            notes: 'Status updated via dashboard'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Client status updated successfully', 'success');
            refreshClientsTable();
        } else {
            showAlert(data.message || 'Error updating status', 'danger');
        }
    })
    .catch(error => {
        console.error('Error updating status:', error);
        showAlert('Error updating client status', 'danger');
    });
}

// Add real-time stats refresh
function refreshDashboardStats() {
    fetch('/clients/api/stats/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateStatsCards(data.stats);
        }
    })
    .catch(error => {
        console.error('Error refreshing stats:', error);
    });
}

// Update stats cards with new data
function updateStatsCards(stats) {
    // Update the numbers in your stats cards
    const metalized = document.querySelector('.stats-card-blue .number');
    if (metalized && stats.metalized_clients !== undefined) {
        metalized.textContent = stats.metalized_clients;
    }
    
    const callbacks = document.querySelector('.stats-card-orange .number');
    if (callbacks && stats.callback_clients !== undefined) {
        callbacks.textContent = stats.callback_clients;
    }
}

// Auto-refresh stats every 30 seconds
setInterval(refreshDashboardStats, 30000);
</script>
"""


# ===== DJANGO SETTINGS UPDATES =====

"""
# Add these to your settings.py:

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    
    # Local apps
    'clients',
    # 'accounts',
    # 'targets',
    # 'payments',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_CREDENTIALS = True

# Login settings
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/clients/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
"""


# ===== COMPLETE SETUP INSTRUCTIONS =====

"""
1. Create the serializers.py file in your clients app
2. Update your views.py with the additional API endpoints
3. Update your urls.py with the complete URL configuration
4. Update your HTML template with the modal and JavaScript code
5. Run migrations:
   python manage.py makemigrations
   python manage.py migrate

6. Install required packages:
   pip install djangorestframework
   pip install django-cors-headers

7. Update your settings.py with the REST framework configuration
8. Create a superuser: python manage.py createsuperuser
9. Test the functionality:
   - Click "Add New Client" button
   - Fill out the form
   - Submit and verify it creates a new client
   - Check that validation works properly

10. Optional: Add logging for debugging:
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Client created: {client.customer_name}")

11. Testing checklist:
    ✓ Modal opens when clicking "Add New Client"
    ✓ Form validation works (required fields, phone format, email format)
    ✓ GST number validation (if provided)
    ✓ Date validation (handover date not in past)
    ✓ Amount validation (advance ≤ total)
    ✓ Team members dropdown loads
    ✓ Form submits successfully
    ✓ Success/error messages display
    ✓ Table refreshes with new client
    ✓ Transfer functionality works
    ✓ Status updates work

12. Common issues and solutions:
    - CSRF token missing: Ensure getCookie function is working
    - 403 Forbidden: Check authentication and permissions
    - 400 Bad Request: Check form validation and data format
    - 500 Server Error: Check Django logs for detailed error
    - Modal not opening: Check Bootstrap JS is loaded
    - Form not submitting: Check JavaScript console for errors
"""


# ===== PRODUCTION CONSIDERATIONS =====

"""
For production deployment, consider these additional configurations:

# settings/production.py
import os
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_MAX_AGE = 31536000
SECURE_HSTS_PRELOAD = True

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/crm/django.log',
        },
    },
    'loggers': {
        'clients': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
"""


# ===== ADVANCED FEATURES TO ADD LATER =====

"""
1. File Upload for Client Documents:
   - Add FileField to Client model
   - Create document upload endpoint
   - Add file management in modal

2. Bulk Operations:
   - Bulk status update
   - Bulk transfer
   - Bulk export to Excel

3. Advanced Search:
   - Search by date range
   - Search by amount range
   - Combined filters

4. Real-time Notifications:
   - WebSocket integration
   - Push notifications for new assignments
   - Email notifications

5. Data Analytics:
   - Client conversion funnel
   - Performance metrics
   - Revenue analytics

6. Mobile Responsiveness:
   - Mobile-first design
   - Touch-friendly interfaces
   - Offline capabilities

7. API Rate Limiting:
   - Django rate limiting
   - API versioning
   - API documentation with Swagger

8. Advanced Validation:
   - Duplicate client detection
   - Phone number verification
   - Email verification

9. Audit Trail:
   - Track all changes
   - User activity logs
   - Data export logs

10. Integration Features:
    - CRM integrations
    - Payment gateway integration
    - Email marketing integration
"""


# ===== TROUBLESHOOTING GUIDE =====

"""
Common Issues and Solutions:

1. Modal not opening:
   - Check if Bootstrap JS is loaded correctly
   - Verify modal ID matches in HTML and JavaScript
   - Check for JavaScript console errors

2. Form submission failing:
   - Verify CSRF token is being sent
   - Check network tab for actual error response
   - Ensure all required fields are filled
   - Validate JSON format being sent

3. Validation errors:
   - Phone number: Must be 10-15 digits, Indian format preferred
   - Email: Standard email format required
   - GST: Must follow GST number pattern if provided
   - Amounts: Total > 0, Advance >= 0, Advance <= Total

4. Team members not loading:
   - Check if users exist in database
   - Verify user permissions
   - Check API endpoint response

5. Database errors:
   - Run migrations: python manage.py migrate
   - Check model constraints
   - Verify foreign key relationships

6. Permission denied errors:
   - Ensure user is authenticated
   - Check view permissions
   - Verify CSRF token

7. Static files not loading:
   - Run: python manage.py collectstatic
   - Check STATIC_URL and STATIC_ROOT settings
   - Verify file paths in templates

8. API endpoint not found:
   - Check URL patterns
   - Verify app URLs are included in main urls.py
   - Check for trailing slashes

Debug commands:
- python manage.py shell (for testing models)
- python manage.py check (for configuration issues)
- python manage.py runserver --verbosity=2 (for detailed logging)
"""


# ===== COMPLETE FILE STRUCTURE =====

"""
Final project structure should look like:

crm_project/
├── manage.py
├── requirements.txt
├── crm_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── clients/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py          # Your existing model
│   ├── views.py           # Updated with API views
│   ├── urls.py            # Complete URL configuration
│   ├── serializers.py     # New file with serializers
│   ├── forms.py           # Optional: Django forms
│   ├── migrations/
│   └── templates/
│       └── clients/
│           └── dashboard.html  # Your HTML with modal
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── media/
└── templates/
    └── base.html

All files are ready for implementation!
"""