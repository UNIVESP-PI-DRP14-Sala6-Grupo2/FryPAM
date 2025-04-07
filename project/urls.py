from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from pam.views import dashboard, cloud_accounts, tenants, login, logout
from pam.views.logout import logout_view
from pam.views.login import login_view
from pam.views.profile import profile_view, edit_profile_view
from pam.views.password_request_views import (
    password_request_list, password_request_create, password_request_detail,
    password_request_approve, password_request_reject, password_request_activate,
    password_withdraw
)
from pam.views.api_views import cloud_account_detail
from project import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard.dashboard_view),
    path('dashboard.html', dashboard.dashboard_view, name='dashboard'),
    path('cloud_accounts.html', cloud_accounts.cloud_accounts_view, name='cloud_accounts'),
    path('password_request.html', password_request_list, name='password_request_list'),
    path('tenants.html', tenants.tenants_view, name='tenants'),
    path('accounts/login/', login.login_view, name='login'),
    path('accounts/logout/', logout.logout_view, name='logout'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('accounts/profile/', profile_view, name='profile'),
    path('accounts/profile/edit', edit_profile_view, name='edit_profile'),
    
    # URLs do sistema de solicitação de senha

    path('password_request/create', password_request_create, name='password_request_create'),
    path('password_request/<int:pk>', password_request_detail, name='password_request_detail'),
    path('password_request/<int:pk>/approve', password_request_approve, name='password_request_approve'),
    path('password_request/<int:pk>/reject', password_request_reject, name='password_request_reject'),
    path('password_request/<int:pk>/activate', password_request_activate, name='password_request_activate'),
    path('password_request/<int:pk>/withdraw', password_withdraw, name='password_withdraw'),
    
    # APIs
    path('api/cloud_accounts/<int:pk>/', cloud_account_detail, name='api_cloud_account_detail'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)