from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def dashboard_view(request):

    content = {
        'title': 'Dashboard',
        'heading': 'Dashboard',
        'active_page': 'dashboard',
        'page': 'dashboard.html',
    }
    return render(request, 'dashboard.html', content)