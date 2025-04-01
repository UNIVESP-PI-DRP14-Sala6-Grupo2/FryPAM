from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', '/')  # Se houver um 'next' na URL, redireciona para ele
                #resolve o bug do next vazio
                if next_url == '': 
                    next_url = '/'
                return redirect(next_url)
            else:
                form.add_error(None, "Credenciais inválidas. Tente novamente.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})
