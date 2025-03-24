from django.shortcuts import render

def dashboard_view(request):


    content = {
        'title': 'Dashboard',
        'heading': 'Dashboard',
        'active_page': 'dashboard',
        'page': 'dashboard.html',
    }
    return render(request, 'dashboard.html', content)