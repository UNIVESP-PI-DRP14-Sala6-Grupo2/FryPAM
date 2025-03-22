
from django.contrib import admin
from django.urls import path, include
from pam.views import base

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path('', base.base_view),

]
