from django.shortcuts import render

def password_requests_view(request):


    content = {
        'title': 'Password Requests',
        'heading': 'Password Requests',
        'active_page': 'password_requests',
    }

    return render(request, 'password_requests.html', content)
