import profile

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import edit

from pam.views import base, dashboard, password_requests, cloud_accounts, tenants, login, profile
from project import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path('', dashboard.dashboard_view),
    path('dashboard.html', dashboard.dashboard_view, name='dashboard'),
    path('password_requests.html', password_requests.password_requests_view, name='password_requests'),
    path('cloud_accounts.html', cloud_accounts.cloud_accounts_view, name='cloud_accounts'),
    path('tenants.html', tenants.tenants_view, name='tenants'),
    path('accounts/login/', login.login_view, name='login'),
    path('accounts/profile/', profile.profile_view, name='profile'),
    path('accounts/profile/edit', profile.edit_profile_view, name='edit_profile'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
