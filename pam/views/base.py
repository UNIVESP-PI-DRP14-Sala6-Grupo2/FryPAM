from django.shortcuts import render
from pam.models import Tenant
from django.contrib.auth.decorators import login_required

#@login_required
def base_view(request):
    return render(request, 'base.html')