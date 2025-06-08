from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('team-members/', views.team_members_view, name='team_members'),
    path('users/', views.UserListView.as_view(), name='user_list'),
]