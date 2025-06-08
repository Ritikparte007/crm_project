from django.shortcuts import render

def dashboard_view(request):
    context = {
        'stats': {
            'total_target': 21000,
            'achieved_target': 0,
            'month_metalized': 3,
            'today_callback': 0,
        },
        'todays_clients': [],
        'transferred_clients': [],
    }
    return render(request, 'dashboard/dashboard.html', context)