# backend/views/login.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages


def login_view(request):
    # Se o método for POST, tentamos autenticar o usuário
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)

        # Verifica se o formulário é válido
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Tenta autenticar o usuário
            user = authenticate(username=username, password=password)

            # Se o usuário for autenticado com sucesso, realiza o login
            if user is not None:
                login(request, user)
                messages.success(request, "Login realizado com sucesso!")
                return redirect('home')  # Ou para qualquer outra página que você desejar após o login
            else:
                messages.error(request, "Credenciais inválidas.")
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")

    # Se o método for GET (ou algum outro), apenas exibe o formulário de login
    else:
        form = AuthenticationForm()

    # Passando o formulário para o template
    return render(request, 'components/login.html', {'form': form})
