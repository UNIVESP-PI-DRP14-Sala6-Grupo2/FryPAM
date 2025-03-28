from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def password_requests_view(request):


    content = {
        'title': 'Password Requests',
        'heading': 'Password Requests',
        'active_page': 'password_requests',
    }

    return render(request, 'password_requests.html', content)
