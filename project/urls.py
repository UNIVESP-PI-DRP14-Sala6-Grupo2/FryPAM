
from django.contrib import admin
from django.urls import path, include
from pam.views import base, dashboard, password_requests, cloud_accounts, tenants

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path('', dashboard.dashboard_view),
    path('dashboard.html', dashboard.dashboard_view),
    path('password_requests.html', password_requests.password_requests_view),
    path('cloud_accounts.html', cloud_accounts.cloud_accounts_view),
    path('tenants.html', tenants.tenants_view),
]
