from django.shortcuts import render


#@login_required
def base_view(request):
    return render(request, 'base.html')