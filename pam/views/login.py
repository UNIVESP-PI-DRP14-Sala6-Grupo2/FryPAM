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
                return redirect('profile')  # Ou 'accounts/profile', dependendo de como está configurado
            else:
                form.add_error(None, "Credenciais inválidas. Tente novamente.")

    else:
        form = AuthenticationForm()

    return render(request, 'components/login.html', {'form': form})
